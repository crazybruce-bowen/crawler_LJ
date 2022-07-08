
a = '''<title>标题</title>
<body>
    <ul class='list1'>
        <li>列表1第1项</li>
        <li>列表1第2项</li>
    </ul>
    <p class='first'>文字1
        <p class='test'>测试
    </p>
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