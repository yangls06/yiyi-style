import base64,io,mimetypes
from PIL import Image
OUT='/Users/deepway/work/yiyi-style/outputs/'
R='/tmp/yiyi/report/'
def b(path):
    return f"data:{mimetypes.guess_type(path)[0] or 'application/octet-stream'};base64,"+base64.b64encode(open(path,'rb').read()).decode()
def j(path,w,q=84,bg='#ffffff'):
    i=Image.open(path).convert('RGBA');i.thumbnail((w,w*3));B=Image.new('RGB',i.size,bg);B.paste(i,(0,0),i)
    o=io.BytesIO();B.save(o,'JPEG',quality=q,optimize=True);return 'data:image/jpeg;base64,'+base64.b64encode(o.getvalue()).decode()
def im(src,cap='',cls=''):
    c=f'<figcaption>{cap}</figcaption>' if cap else ''
    return f'<figure class="{cls}"><img loading="lazy" src="{src}" alt="{cap[:40]}">{c}</figure>'
fp=OUT+'font/yiyi-general.woff2'
S=OUT+'stickers/png/'
pairs=[('clay_chick','02_发芽啦','小鸡：球身、大圆鼻喙、刻线翅膀'),('clay_bunny','05_想你','粉团兔：原作没有脸，五官是新加的'),('clay_ghost','12_我来了','蘑菇帽幽灵：波浪帽檐、蝴蝶结、淡腮红'),('clay_pika','14_潮来了','泳池里的电气鼠：她的皮卡丘同人作品')]
pair_html=''.join(f'<div class="pair"><img loading="lazy" src="{b(R+a+".jpg")}" alt="原作"><img loading="lazy" src="{j(S+c+".png",420,bg="#d9e8dc")}" alt="重建"><p>{t}</p></div>' for a,c,t in pairs)
gifs=''.join(f'<img loading="lazy" src="{b(OUT+"stickers/gif/"+n+".gif")}" alt="动图表情">' for n in ['01_你好','06_不要','15_早上好','12_我来了'])
H=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>把孩子的作业和手工，做成一套字体和表情</title>
<style>
@font-face{{font-family:YiyiHand;src:url({b(fp)}) format("woff2")}}
:root{{--ink:#26232a;--mut:#6d6873;--line:#e4dfd2;--bg:#fbf8ef;--card:#fff;--acc:#1f55b8}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.8 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
main{{max-width:880px;margin:auto;padding:24px 22px 90px}}
header{{padding:56px 0 20px}}h1{{font-size:38px;line-height:1.3;margin:0 0 14px}}h2{{font-size:27px;margin:64px 0 12px;padding-top:18px;border-top:1px solid var(--line)}}h3{{font-size:19px;margin:32px 0 6px}}
.lead{{font-size:19px;color:var(--mut)}}.hand{{font-family:YiyiHand,serif}}
figure{{margin:20px 0}}figure img{{width:100%;display:block;border:1px solid var(--line);border-radius:8px;background:#fff}}figcaption{{font-size:14px;color:var(--mut);margin-top:6px;line-height:1.6}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}.g3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.g2 figure,.g3 figure{{margin:8px 0;min-width:0}}pre,table{{max-width:100%}}td{{overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%;font-size:15px;margin:16px 0}}th,td{{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}th{{color:var(--mut);font-weight:600}}
.nums{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:26px 0}}.nums div{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;font-size:14px;color:var(--mut)}}.nums b{{display:block;font-size:28px;color:var(--ink);line-height:1.3}}
ol.flow{{padding-left:22px}}code{{background:#f1ecdf;padding:1px 5px;border-radius:4px;font-size:.88em}}pre{{background:#2a2730;color:#f2eee4;padding:14px 16px;border-radius:8px;overflow:auto;font-size:14px;line-height:1.6}}
.note{{background:#fff;border-left:3px solid var(--acc);padding:10px 16px;margin:18px 0;font-size:15.5px}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0}}.pair img{{width:100%;border-radius:8px;border:1px solid var(--line);display:block}}.pair p{{grid-column:1/3;margin:0 0 14px;font-size:14px;color:var(--mut)}}.pairs{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:16px}}
.gifs{{display:flex;flex-wrap:wrap;gap:12px;background:#d9e8dc;padding:14px;border-radius:8px;justify-content:center}}.gifs img{{width:170px;height:170px}}
textarea{{width:100%;min-height:150px;border:1px solid var(--line);border-radius:8px;background:#fff;padding:14px 16px;font:38px/1.6 YiyiHand,serif;color:var(--ink);resize:vertical}}
.rot{{font:44px/1.5 YiyiHand,serif;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 16px;margin:14px 0;letter-spacing:.04em}}.rot small{{display:block;font:14px/1.6 -apple-system,"PingFang SC",sans-serif;color:var(--mut);letter-spacing:0}}
@media(max-width:640px){{h1{{font-size:29px}}.nums{{grid-template-columns:1fr 1fr}}.g3,.g2,.pairs{{grid-template-columns:1fr}}}}
</style></head><body><main>
<header><h1>把孩子的作业和手工，做成一套字体和表情</h1>
<p class="lead">从 65 张手机照片出发，提取 yiyi 的汉字、数字、英文笔迹做成字体，并把她的笔法泛化到 3758 个常用字，再分析她的画和黏土手工，做成 24 个 emoji 和 16 张表情包。这里记录方法、过程和走过的弯路。</p></header>
<div class="g2">{im(b(OUT+'font/specimen-raw.png'),'yiyi-raw：只收她亲手写的字')}{im(b(OUT+'font/specimen-general.png'),'yiyi-general：按她的笔法泛化到 3758 个常用字')}</div>
<div class="g2">{im(j(OUT+'emoji/overview.png',1000),'24 个纸片 emoji')}{im(j(OUT+'stickers/overview.png',1000,bg='#cfe3d4'),'16 张黏土表情包')}</div>
<div class="nums"><div><b>65</b>张原始照片</div><div><b>3184</b>个切出的格子</div><div><b>458</b>个她写过的汉字</div><div><b>3758</b>个泛化后的汉字</div></div>

<h2>1. 素材：先看清手里有什么</h2>
<table><tr><th>类别</th><th>张数</th><th>内容</th><th>用途</th></tr>
<tr><td>语文</td><td>16</td><td>作文和听写，14 页不重复，有 2 页重拍</td><td>汉字</td></tr><tr><td>数学</td><td>22</td><td>口算和练习册</td><td>数字</td></tr><tr><td>英语</td><td>8</td><td>练习册上的铅笔填空</td><td>英文</td></tr><tr><td>画画</td><td>5</td><td>披萨、奶茶、甜筒、大眼角色的剪纸小标签</td><td>emoji</td></tr><tr><td>手工</td><td>14</td><td>4 个黏土角色的多角度照片</td><td>表情包</td></tr></table>
<p>难点在于一页上混着好几个人的字：印刷体、老师的红笔、修改符号拉出的圈字、她的铅笔字和订正。字体只能用她写的，所以第一件事是区分。</p>

<h2>2. 区分谁写的</h2>
<p>颜色能解决一大半，剩下的靠人工判断规则：</p>
<table><tr><th>内容</th><th>怎么认</th><th>处理</th></tr>
<tr><td>她的字</td><td>格子里的铅笔、蓝笔订正、黑笔作文</td><td>保留</td></tr><tr><td>老师批改</td><td>红笔，LAB 色彩空间里 a 通道明显偏高</td><td>按颜色去除，红线压字的样本降权</td></tr><tr><td>圈字改字</td><td>带圈或修改符号，颜色和她的笔一样</td><td>转录时人工跳过</td></tr><tr><td>涂黑、划掉</td><td>她自己写错的部分</td><td>转录时人工跳过</td></tr><tr><td>绿色格线</td><td>a 通道偏低</td><td>只在格子边缘附近去除</td></tr></table>
<div class="g2">{im(b(R+'layer_a.jpg'),'原始照片')}{im(b(R+'layer_b.jpg'),'按颜色分层：深蓝是笔迹，红色是批改，绿色是格线。整页阈值还有不少噪点，所以后面改成逐格处理。')}</div>

<h2>3. 汉字：从照片到字形</h2>
<h3>第一步：顺着格线把纸“拉平”</h3>
<p>作业本是弯的，还拍斜了，直接切格子会切歪。绿色格线正好是现成的坐标系：追踪每条横线，拟合三次曲线，再把每一行拉直，在行内找竖线，就能得到每个格子四个角的位置。</p>
<div class="g2">{im(b(R+'grid.jpg'),'追踪到的横向格线（红色），能贴合纸面弯曲')}{im(b(R+'strip.jpg'),'拉直后的行条，带行列编号，用来逐格转录')}</div>
<h3>第二步：逐格转录</h3>
<p>我试过 Apple Vision 的手写 OCR，错字和漏字都太多，最后没有采用。改成由 Claude 读行条图，把每格写成一行字符串，<code>_</code> 表示空格或要排除的格子：</p>
<pre>'5362': {{ 4: '我准备观察绿豆。_先我拿了一些',
          5: '绿豆泡水，我等啊等，绿豆还是没', ... }}</pre>
<p>这样既得到每格的标签，也完成了人工筛选。之后再生成带标签的核对图，抓出了几处错位。</p>
<h3>第三步：提取和统一笔画</h3>
{im(b(R+'stages.jpg'),'从左到右：原始格子 → 提取墨迹 → 取骨架后重新描笔 → 字体里的字形')}
<p>铅笔、蓝笔和黑笔的粗细不同，放进一个字体会显得杂乱。做法是先取笔画中心线，再用统一的笔宽重新描一遍，并保留一部分她原有的轻重变化，最后转成矢量轮廓。</p>
<h3>第四步：同一个字选最好的样本</h3>
<p>共有 1340 个可用样本。系统黑体只用来判断笔画是否完整，字形本身不用。分数最高的不一定最好看，所以我又看了全部 458 个字，用手动规则换样本、裁残留格线或提高阈值。</p>
{im(b(R+'samples.png'),'「绿」字的 13 个样本。自动评分选了第 1 个，缺笔明显；人工改选第 2 个。')}

<h2>4. 数字和英文</h2>
<h3>数字：好认</h3>
<p>她的数字窄长、带弯，和印刷体差别很大。按连通块切出候选，人工挑出每个数字的 2 种写法。</p>
{im(b(R+'digits.jpg'),'候选连通块，手写和印刷、汉字混在一起，需要人工挑选')}
<h3>英文：最难，走了弯路</h3>
<p>她的字母骑在印刷的基线和虚线上，铅笔和印刷线几乎连成一体。试过按明暗分离，笔芯被挖空；又试过去除通栏横线，横笔跟着没了，因为四线格的虚线和 t、H 的横笔高度正好重合。</p>
<div class="g2">{im(b(R+'en_fail.jpg'),'第一次尝试：按明暗分离，笔画被挖空，基线也没去干净')}{im(b(R+'letters_fail.png'),'第二次尝试：去除通栏横线后，t、H 的横笔丢了，e、s、w 还粘着基线')}</div>
<p>继续调参不划算，于是分三路处理，并把来源如实记录：</p>
<table><tr><th>来源</th><th>字符</th></tr><tr><td>直接提取她的笔迹（7）</td><td>d h k n y S B</td></tr><tr><td>放大原图逐点描线（20）</td><td>a b c e f g i l m o p r s t u w H A C E</td></tr><tr><td>她没写过，按笔法补画（26）</td><td>j q v x z 和其余 21 个大写</td></tr></table>
{im(b(R+'trace_overlay.jpg'),'描线（红色）叠回原照片核对。第一次核对发现 A、p、u 的笔画描偏，修正后才定稿。多数字母贴合；u 的底部连笔是推断的，i 的点在裁切框外，也是补的；a、b 不在这张图里，没有经过这一步核对。')}

<h2>5. 打包成字体</h2>
<p>用 potrace 把位图转成矢量，再用 fontTools 编译成 TTF 和 WOFF2。常用字有 2–3 个样本，就都放进字体，用 OpenType 的 <code>calt</code> 功能轮换，避免重复的字一模一样。下面这行就是实时渲染的：</p>
<div class="rot">的的的的的的 爷爷爷爷 2222<small>同一个字连续出现时，每个写法都略有不同</small></div>
<h3>自己试试</h3>
<textarea aria-label="用 Yiyi 手写体试写">绿豆发芽了！
我的爷爷每天早上五点就起床。</textarea>
<p style="font-size:15px;color:var(--mut)">这里用的是 yiyi-general：她写过的 458 字用原迹，其余 3300 个常用字是按她的笔法生成的，见第 8 节。</p>

<h2>6. 绘画：提炼规则，再画新的</h2>
<div class="g2">{im(b(R+'draw_food.jpg'),'原作：披萨、奶茶和甜筒')}{im(b(R+'draw_char.jpg'),'原作：大眼角色')}</div>
<p>没有直接描她的画，而是总结出规则，再写进绘图程序：</p>
<table><tr><th>观察到的特点</th><th>程序里怎么实现</th></tr>
<tr><td>黑色细笔，线条微抖，收笔出头，闭合不严</td><td>给线条加低频抖动和压力变化，末端多画一小段</td></tr><tr><td>沿外形留白，剪刀剪出折线</td><td>外扩后再简化成多边形</td></tr><tr><td>物体总是歪着放</td><td>每个图案有自己的倾斜角度</td></tr><tr><td>用点、短线、网格填满细节</td><td>奶茶珍珠、甜筒网格、草莓籽</td></tr><tr><td>只用一支彩笔</td><td>全套只用黑色加一种蓝</td></tr><tr><td>超大圆眼，瞳孔外斜，睫毛短线</td><td>表情脸的通用模板</td></tr></table>
{im(j(OUT+'emoji/overview.png',1100),'全部 24 个 emoji，每个都有 SVG 和 PNG')}

<h2>7. 手工：用 3D 重建黏土角色</h2>
<p>表情包需要同一角色摆出不同表情和动作，只抠照片做不到。所以用有符号距离场（SDF）和光线步进写了一个小渲染器，角色由椭球、胶囊等形状组成，表情和动作都是参数。</p>
<p>超轻黏土的质感靠这几点：多层噪声扰动法线做出细绒，完全不用镜面高光，用环绕光和环境光遮蔽做出柔和的明暗。</p>
<div class="pairs">{pair_html}</div>
<p>配文大多取自她作文里的词句，比如“发芽啦！”“风平浪静”“潮来了！”，用的是她的字体。第 13–16 张的角色是皮卡丘同人，只适合私下使用。</p>
<div class="gifs">{gifs}</div>

<h2>8. 泛化：从 458 字扩到 3758 字</h2>
<p>458 字只占常用字的约 12%。为了日常可用，又做了第二个字体，把她的笔法迁移到她没写过的字上。方法分三步：</p>
<ol class="flow"><li><b>对齐</b>：借助开源笔画数据 Make Me a Hanzi，它给每个字提供了标准笔画的中心线。把标准骨架对齐到她写的 712 个样本上，再让每一笔吸附到她的墨迹上，就能量出“她这一笔和标准写法差多少”。</li>
<li><b>建笔画库</b>：按“在哪个部件、第几笔”归档这些差异。例如她写“纟”的第一笔怎么拐、“口”的右上角怎么收，都能单独查到。</li>
<li><b>生成</b>：新字先拆成部件。部件她写过，就借用她写这个部件时的笔画差异；没写过，就找形状最像的笔画。整体的宽高比、倾斜和摆放也来自她真实的书写。</li></ol>
{im(b(R+'reg.png'),'对齐效果：蓝线是标准骨架，红线是吸附到她墨迹上的笔画')}
<p>为了验证，每次拿走一个她写过的字，只用其余的字去生成它，再和真迹比较：</p>
{im(b(R+'loo.png'),'每组左边是真迹，右边是“没见过这个字”时生成的结果；角标是能借用同部件笔画的比例')}
{im(b(R+'gen_para.png'),'混排效果：蓝色是她的原迹，黑色是生成的字')}
{im(b(R+'gen_rand.png'),'随机抽取的 240 个生成字')}
<div class="note">生成的字是“像她写的”，不是她写的。它们比真迹更规整，少了随手的歪斜和抖动。所以分成两个字体：<b>yiyi-raw</b> 只收她的原迹，<b>yiyi-general</b> 用于日常打字。</div>

<h2>9. 踩过的坑</h2>
<table><tr><th>现象</th><th>原因</th><th>解决</th></tr>
<tr><td>很多行没切出来</td><td>稿纸有 300 格和 225 格两种，行高不同</td><td>按每页的间距分布自动判断</td></tr>
<tr><td>铅笔字缺笔</td><td>去绿线的规则误伤了淡笔画</td><td>只在格线附近去绿</td></tr>
<tr><td>字上带格线</td><td>个别行的格线偏移，不在预期位置</td><td>加宽检测范围，再逐字裁切</td></tr>
<tr><td>字体渲染成黑块</td><td>potrace 的位图极性反了</td><td>取反</td></tr>
<tr><td>句号旁多一竖</td><td>标点格子混入了邻字的笔画</td><td>标点改为按她的笔法绘制</td></tr>
<tr><td>写法不轮换</td><td>规则写错，实际全部用同一变体。HarfBuzz 排版测试才发现</td><td>改为根据前一个字的状态轮换</td></tr>
<tr><td>She 变成 Sle</td><td>去噪点时只留最大连通块，h 的右半边被丢掉</td><td>改成只丢很小的碎块</td></tr>
<tr><td>A、p、u 描偏</td><td>只凭网格读坐标</td><td>叠回原图核对后修正</td></tr></table>

<h2>10. 局限和下一步</h2>
<ul><li><b>原迹字数少</b>：yiyi-raw 只有 458 字。再拍课文抄写和生字本，用同一流程就能扩充，生成字也会因笔画库变大而更像她。</li><li><b>生成字更规整</b>：缺少她真迹里随手的不稳定感；GB2312 一级以外的字仍然没有。</li>
<li><b>英文不全是原迹</b>：真正直接提取的只有 7 个字母，其余靠描线或补画。如果她在白纸上写一遍大小写字母表，就能全部换成原迹。</li>
<li><b>风格化的边界</b>：emoji 和表情包是按规则新做的，不是 AI 生图，也不是她的原作，只是学习她的特点。</li>
<li><b>少数字质量一般</b>：堵、翻、犹、移、接只有一个写得较粗的样本，放大后不够干净。</li></ul>
<h3>用到的工具</h3>
<p>Python、OpenCV、scikit-image、SciPy、potracer、fontTools、HarfBuzz、NumPy，笔画数据来自 Make Me a Hanzi（hanzi-writer-data），全部在本地运行。方案、转录和代码由 Claude Code 完成，yiyi 的作品是这一切的来源。</p>
</main></body></html>'''
open(OUT+'process.html','w').write(H);print(len(H)/1e6,'MB')
