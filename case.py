a = '''<title>标题</title>
<body>
    <ul class='list1'>
        <li>列表1第1项</li>
        <li>列表1第2项</li>
    </ul>
    <p class='first'>文字1</p>
    <p class='second'>文字2</p>
    <ul class='list2'>
        <li>列表2第1项</li>
        <li>列表2第2项</li>
    </ul>
</body>'''

from pyquery import PyQuery as pq

doc = pq(a)
doc('title').text() # '标题'
doc('p').filter('.first').text() # '文字1'
doc('p[class=first]').text() # 同上，只是这种方法支持除了id和class之外的属性筛选
doc('p').text() # '文字1 文字2'
doc('ul').filter('.list1').find('li').text() # '列表1第1项 列表1第2项'
doc('ul.list1 li').text() # 简化形式
doc('ul.list1 > li').text() # 节点之间用>连接也可以，但是加>只能查找子元素，空格子孙元素

# ==========

a = '''
<body>
    <h><a href='www.biaoti.com'>head</a></h>
    <p>段落1</p>
    <p>段落2</p>
</body>
'''

doc = pq(a)
# 提取标签内容
doc('h').text() # 'head'
doc('h').html() # '<a href="www.biaoti.com">head</a>'
doc('body').html() # '\n    <h><a href="www.biaoti.com">head</a></h>\n    <p>段落1</p>\n    <p>段落2</p>\n'
doc('p').text() # '段落1 段落2'
doc('p').text().split(' ') # ['段落1', '段落2']
doc('p:nth-of-type(1)').text() # '段落1'
doc('body').text() # 'head 段落1 段落2'

# 提取标签属性
doc('h a').attr('href') # 'www.biaoti.com'

# ===========================

a = '''
<body>
    <h1>head</h1>
    <h2>标题2</h2>
    <h2>标题3</h2>
</body>
'''

doc = pq(a)
doc('h1').text() # 'head'
doc('h1, h2').text() # 表示“或”用逗号 'head 标题2 标题3'

# =================================

a = '''
<body>
    <h>标题</h>
    <p id='p1'>段落1</p>
    <p id='p2'>段落2</p>
    <p class='p3'>段落3</p>
    <p class='p3' id='pp'>段落4</p>
</body>
'''

doc = pq(a)
doc('p#p1').text() # '段落1'
doc('p.p3[id]').text() # 含有id属性
doc('p.p3#pp').text() # 使用多个属性筛选
doc('p[class=p3][id=pp]').text()
doc('p[class=p3], p[id=p1]').text() # 或的关系
doc('p[class=p3],[id=p1]').text() # 或者只用,隔开
doc('*#p1').text() # 不指定标签名

# 否定
doc('p:not([id])').text() # 不含有id属性
doc('body :not(p)').text() # 选出不是p的子节点  '标题'
doc('p:not(.p3)').text() # 选出class不是p3的
doc('p[id][id!=p2]').text() # 也可以用!=，这里选择有id且id不是p2的

# 类似正则表达式
doc('p[id^=p]').text() # 首端匹配
doc('p[id$=p]').text() # 尾端匹配
doc('p[id*=p]').text() # 包含

# =================================

a = '''
<p id='p1'>段落1</p>
<p class='p3'>段落2</p>
<p class='p3'>文章</p>
<p></p>
'''

doc = pq(a)
# :contains查找内容中包含某字符串的标签
doc('p:contains(段落1)').text() # '段落1'
doc('p:contains(段落)').text() # '段落1 段落2'
doc('p:contains("1")').text()

# ===========================

a = '''<title>标题</title>
<body>
    <ul class='list1'>
        <li>列表1第1项</li>
        <li>列表1第2项</li>
    </ul>
    <p class='first'>文字1</p>
    <p class='second'>文字2</p>
    <ul class='list2'>
        <li>列表2第1项</li>
        <li>列表2第2项</li>
    </ul>
</body>'''

doc = pq(a)
doc('ul:nth-of-type(2) li').text() # 选择第二个ul下的所有li
doc('ul li:nth-of-type(2)').text() # 选择每个ul中第二个li
doc('ul li:even').text() # :even取偶数  :odd取奇数（这里索引第一个是0）
doc('ul li:first').text() # :first取第一个 :last取最后一个
doc('ul li:eq(0)').text() # 还有 lt gt 索引从0开始
