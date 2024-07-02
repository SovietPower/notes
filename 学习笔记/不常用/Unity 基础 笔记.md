# Unity 基础 笔记

---

[TOC]

---

## 玩家操作

**操作输入 - 按键检测**

通过`Input.GetKey(KeyCode.LeftControl)`可以简单获取某个按键信息。
GetKey 为按住就生效，GetKeyDown 在按下的第一帧生效，GetKeyUp 在松开的第一帧生效。

**操作输入 - 虚拟轴**

>https://docs.unity3d.com/cn/2019.4/Manual/class-InputManager.html
>https://blog.csdn.net/konkon2012/article/details/130599525

Edit > Project Settings > Input Manager 中定义了若干输入轴，通过配置和使用它们，可以实现不同输入方式、灵活更改输入方式（不是在代码中写死某个 key）。
同时定义了 Positive、Negative Button 的轴一般用于移动操作，通过`Input.GetAxis ("Horizontal")`获取该轴当前的浮点数值。通过设置 type 可接收鼠标、手柄移动信息。
只定义了 Positive Button 的轴用于点击事件，通过`Input.GetButtonDown("Fire")`获取该轴当前的 bool 输入。

**人物移动**







## 视角

**摄像机跟随玩家**

给相机一个脚本，让它在 Update 中随玩家移动即可。

```c#
public class CameraScript_1 : MonoBehaviour
{
    public GameObject target;
    public float smooth = 2f;
    Vector3 distance;
    
    void Start()
    {
        // 初始化 target 或 target.transform
        distance = transform.position - target.transform.position;
    }
 
    void LateUpdate()
    {
        transform.position = Vector3.Lerp(target.transform.position+distance, transform.position, Time.deltaTime * smooth); // 可以平滑也可直接移动
        transform.LookAt(target.transform.position); // 过程中摄像头可以看向物体
    }
}
```





## 音频

要做的类似 AudioSource.PlayClipAtPoint，但它只能设置音量不能设置其它参数，所以要自己实现个。
首先创建 AudioSource 对象池，减少开销；然后每次调用 AudioManager.PlayAt 就取出一个 AudioSource，设置位置、将 Sound 相关参数赋值，然后 Play。

在 Gameroot 下设置 AudioListener，然后用脚本跟随玩家位置。缺点是需要时刻判断玩家 transform 是否存在；当玩家新建时由 GameManager 通知它更新玩家 transform。

~~玩家、敌人等 Agent 类运行时自动生成一个 AudioSource，Agent 发出的音效都由自己的 Source 播放，以实现 3D 效果。其它音效如果非 3D，则由 AudioManager 播放，否则由 AudioManager 的 PlayAt 播放。~~

~~为 Gameroot 和 Player 设置 AudioListener，当 Player enable 时，使用 Player 的 Listener、禁用 Gameroot 的；当 Player disable 时，激活 Gameroot 的。这样 1 不需要 Gameroot 跟随玩家位置（玩家新建或不存在时需要额外处理），2 可以玩家不存在、场景切换时也能听到音效。~~











