# Folly HazardPointer
Tags: 实习 2022.7 华为

------------
[TOC]

------------

实现包含[`Hazptr.h`](https://github.com/facebook/folly/blob/main/folly/synchronization/Hazptr.h)中的所有`.h`文件。

----------
### 总结
与论文和[之前看的实现](https://github.com/bhhbazinga/HazardPointer/blob/master/reclaimer.h)相比，folly 主要是：

- 实现了给待回收对象绑定 cohort 或进行标记，允许相关的对象被划分到相同的 cohort，由 cohort 一起回收；允许用户随时主动回收带有指定标记的所有对象。
- 允许使用线程本地存储作为缓存。HP、HP holder 会先使用 TLS 中的可用对象，然后再去全局取。
- 允许指定回收顺序，可保证一些对象在另一些对象回收完后才准备回收。

------------

### HazptrRec.h
`class hazptr_rec`
保存真正的 HP。

```
Atom<const void*> hazptr_{nullptr}; // hazard pointer
hazptr_domain<Atom>* domain_; // 所属 domain
hazptr_rec* next_; // 在 HP 链表中的 next。不可变
hazptr_rec* nextAvail_{nullptr}; // 在 HP 链表中的下一个可用 HP
```

------------
### HazptrHolder.h
`class hazptr_holder`
外部实际使用的 HP 容器。提供操作 HP 的接口；在初始化/析构时自动获取/释放 HP（均为`hazptr_rec`）。

**`make_hazard_pointer(hazptr_domain<Atom>& domain)`**
创建属于指定 domain 的 HP 的 holder。
如果定义了线程本地存储（`#if FOLLY_HAZPTR_THR_LOCAL`）且所属的 domain 为默认 domain，则尝试从线程本地缓存中取一个 HP；如果取不到或未定义，则在 domain 中请求一个。
```cpp
template <template <typename> class Atom>
FOLLY_ALWAYS_INLINE hazptr_holder<Atom> make_hazard_pointer(
		hazptr_domain<Atom>& domain) {
	#if FOLLY_HAZPTR_THR_LOCAL
	if (LIKELY(&domain == &default_hazptr_domain<Atom>())) {
		auto hprec = hazptr_tc_tls<Atom>().try_get();
		if (LIKELY(hprec != nullptr)) {
			return hazptr_holder<Atom>(hprec);
		}
	}
#endif
	auto hprec = domain.acquire_hprecs(1);
	DCHECK(hprec);
	DCHECK(hprec->next_avail() == nullptr);
	return hazptr_holder<Atom>(hprec);
}
```

**`~hazptr_holder()`**
释放 holder 及其持有的 HP。
如果定义了线程本地存储（`#if FOLLY_HAZPTR_THR_LOCAL`）且所属的 domain 为默认 domain，则尝试将 HP 放入线程本地缓存。否则释放该 HP。

**`void reset_protection(const T* ptr)`**
设置 HP 为指定值。
传入 nullptr 即清空该 HP。

**`bool try_protect(T*& ptr, const Atom<T*>& src, Func f)`**
尝试设置 HP 为`src`指向的值`ptr`（也即保护`ptr`）。
```cpp
template <typename T, typename Func>
FOLLY_ALWAYS_INLINE bool try_protect(T*& ptr, const Atom<T*>& src, Func f) noexcept {
	/* Filtering the protected pointer through function Func is useful
			for stealing bits of the pointer word */
	auto p = ptr;
	reset_protection(f(p));
	/*** Full fence ***/ folly::asymmetric_thread_fence_light(
			std::memory_order_seq_cst);
	ptr = src.load(std::memory_order_acquire);
	if (UNLIKELY(p != ptr)) {
		reset_protection();
		return false;
	}
	return true;
}
```

`Func f`一般就是`[](T* t) { return t; }`。还可用来清除指针中可能存在的标记位。

会加入一个内存屏障，重新检查`src`处的值是否发生改变。如果发生改变则清空 HP，返回false。
\*不是很懂这一步的必要性。

**`T* protect(const Atom<T*>& src, Func f)`**
设置 HP 为`src`指向的值`ptr`（也即保护`ptr`）。
即不断`try_protect(ptr, src, f)`，直到成功。

------------
### HazptrThrLocal.h
`class hazptr_tc`
线程本地缓存 (thread cache)，缓存属于默认 domain 的 HP。
使用该类时，均通过`hazptr_tc_tls()`调用其单例。
```cpp
static constexpr uint8_t kCapacity = 9;

hazptr_tc_entry<Atom> entry_[kCapacity]; // 可用 HP 对象池
uint8_t count_{0}; // 可用 HP 数量
```

**`hazptr_tc<Atom>& hazptr_tc_tls()`**
返回线程本地的`hazptr_tc`单例。
```cpp
template <template <typename> class Atom>
FOLLY_ALWAYS_INLINE hazptr_tc<Atom>& hazptr_tc_tls() {
	return folly::SingletonThreadLocal<hazptr_tc<Atom>, hazptr_tc_tls_tag>::get();
}
```

**`hazptr_rec<Atom>* try_get()`**
尝试从缓存中获取一个 HP。失败返回 nullptr。

**`bool try_put(hazptr_rec<Atom>* hprec)`**
尝试在缓存中添加一个 HP。失败（已满）返回 false。

**`void fill(uint8_t num)`**
创建并在缓存中填充指定数量的 HP。


------------
### HazptrUtils.h
提供`linked_list`、`shared_head_tail_list`、`shared_head_only_list`三种链表。
链表只支持`push`和`pop_all`。

**`class linked_list`**
普通的链表。不保证并发安全，不用做共享变量。

**`class shared_head_tail_list`**


------------
## 对比
于[之前看的实现](https://github.com/bhhbazinga/HazardPointer/blob/master/reclaimer.h)（下称为 reclaimer）作了对比。后者简单直观，很贴近论文和一般认识。

**tag**
folly 

**retired objects**
reclaimer 将所有待回收对象放到一个哈希表中。
folly 的待回收对象通过保存`next`连成链表。
（个人理解）链表有用的点在于，仅通过一个`head` 就可指定并回收一系列对象。回收完一条链时，可获取要后于它回收的 children 链，继续回收它们。
```
// 回收一个链表中的对象。
// 若这些对象回收时的 children 不为空：若 cohort 仍 active，将其加入默认 domain；否则在此处就进行回收。
void reclaim_list(Obj* obj) {
	while (obj) {
		hazptr_obj_list<Atom> children;
		while (obj) {
			Obj* next = obj->next();
			(*(obj->reclaim()))(obj, children);
			obj = next;
		}
		if (!children.empty()) {
			if (active()) {
				hazptr_domain_push_retired<Atom>(children);
			} else {
				obj = children.head();
			}
		}
	}
}
```

**HP**
reclaimer 使用全局的 HP 链表，获取时找一个不用的。新建时直接放入。
folly 首先尝试从线程本地存储中取一个 HP，然后再尝试从全局的可用 HP 链表取：HP 本身保存了`next`，可直接取出。

**HP holder**
folly 也在本地给`hazptr_holder`建了对象池。



