# 语言：Python 杂

---

[TOC]

---

## 一些笔记



- 函数、类、或模块会创建变量作用域，而 if、for 不会，因此两个同一函数内的独立的 if/for 可以使用同一个变量，但必须保证使用时该变量已定义。
- 函数在使用前必须定义；可以在循环中定义函数，每次循环时函数都会被定义一遍。
- python 子类覆盖父类函数不需要也没有 override。[3.12](https://peps.python.org/pep-0698/) 加入了 `@override` 修饰器。











---

## 一些代码

**获取函数名**

```python
def get_function_name(depth=1):
    """
    获取调用堆栈中指定深度的函数名。
    depth=1 表示获取调用者的函数名，depth=2 表示获取调用者的调用者的函数名，依此类推。
    """
    frame = inspect.currentframe()
    for _ in range(depth):
        frame = frame.f_back
    return frame.f_code.co_name
```

**获取调用栈**

输出与 python 抛异常时一样：

```python
def print_call_stack(limit=None, start=None):
    stack = traceback.format_stack()[:-1] # 忽略 format_stack() 这层调用
    # 从第 start 层开始输出（默认是 1）
    if start is not None:
        stack = stack[:-start+1]
    # 只保留 limit 层，如果 limit 为 None，则保留所有层
    if limit is not None:
        stack = stack[-limit:]
    print("Current call stack:")
    for line in stack:
        print(line.strip())
```

**logging**

```python
class CriticalHandler(logging.Handler):
    def emit(self, record):
        if record.levelno == logging.CRITICAL:
            sys.stderr.write('Critical error: ' + self.format(record) + '\n')
            sys.exit(1)

def gen_logger(name):
    '生成与 root logger 独立的 logger'
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	stream_handler = logging.StreamHandler(sys.stdout)
	stream_handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter('[%(levelname)s] [%(filename)s:%(lineno)d, %(funcName)s] %(message)s')
	stream_handler.setFormatter(formatter)
	logger.addHandler(stream_handler)

	critical_handler = CriticalHandler()
	critical_handler.setLevel(logging.CRITICAL)
	logger.addHandler(critical_handler)

	logger.propagate = False # 避免 root logger 再输出一遍该 logger 的 msg
	return logger

logger = gen_logger('util')
```

**logger.every_n**

```py
class ConditionalLogger:
  def __init__(self, logger, should_log):
    self.logger = logger
    self.should_log = should_log

  def __getattr__(self, name):
    if self.should_log:
      return getattr(self.logger, name)
    else:
      return lambda *args, **kwargs: None

class CustomLogger(logging.Logger):
	def __init__(self, name, level=logging.NOTSET):
		super().__init__(name, level)
		self.counter = {}

		# should_log 只有两种取值，预先创建好所有 ConditionalLogger 对象
		self.c_logger = {
			False: ConditionalLogger(self, False),
			True: ConditionalLogger(self, True),
		}

	def _find_caller(self):
		frame = sys._getframe(2)  # 上上个调用者
		while frame:
			code = frame.f_code
			return (code.co_filename, frame.f_lineno)
			# if os.path.join("utils", "logger.") not in code.co_filename:
			#   return code.co_filename, frame.f_lineno, code.co_name
			frame = frame.f_back

	def every_n(self, n, custom_key = None):
		key = self._find_caller()
		if custom_key is not None:
			key = (key, custom_key)
		if key not in self.counter:
			self.counter[key] = 0
		should_log = self.counter[key] % n == 0
		self.counter[key] += 1
		return self.c_logger[should_log]
		# return ConditionalLogger(self, should_log)

	def check(self, should_log):
		return self.c_logger[should_log]

logging.setLoggerClass(CustomLogger)
logger = logging.getLogger(name)

logger.every_n(10).info("xxx")
logger.every_n(20, custom_key=f"{metric_name}").info("xxx")
```


**list 相加**

- `a += b` 或 `a.extend(b)` 会在 a 的基础上拷贝 b，效率最高，但无法复用 a。
  - 如果要保留 a，注意`r = a, r.extend(b)` 不行，会浅拷贝并修改 a，和前面实际一样。

- `a + b` 会创建新的 list 并将 a,b 中的元素依次拷贝过去，效率较低（但如果要保留 a 则没办法）。
- `r = a.copy(), r.extend(b)` 或 `a.extend(b), a = a[:-1]` 效率最低，前者 copy 后再进行一次扩展，不如直接加；后者仍会有 copy 且引入切片。









---

## end





