import random
from random import randint

# random.randrom()，括号中不填参数
# 生成0到1直接之间的随机实数，区间[0,1)

# random.randint(0,100)
# 生成0到100直接之间的随机整数，区间[0,100]

# random.randrange(0,100)，第一个参数可以省略，默认0
# 生成0到100直接之间的随机整数，区间[0,100)

# random.uniform(0,100)
# 生成0到100直接之间的随机浮点数，区间[0,100]

# random.choice(list/tuple/string)
# 从给定的列表/元组/字符串中随机选中一个元素返回

# secrets.choice(list/tuple/string)
# 从给定的列表/元组/字符串中随机选中一个元素返回

# secrets.randbelow(100)，括号中只有结束数字，没有开始数字，默认从0开始
# 返回0到100之间的随机整数，区间[0,100)

