# 纠音表（唯一来源）

报告里一切「怎么发这个音」的说法——老师说、小目标、在家练——**只能从这张表取**，原句照抄「纠音说法」一栏，不许临场改写或自编（「舌头捋直」「嘴巴张大」这类说法就是这样来的）。表里没有的音，只给对比词听辨跟读，不写发音部位。

用法：先诊断（目标音 → 孩子发成了什么），在下表找到对应的行，把行首的键写进 `case.json` 的 `focus_sound.target`；例词写进 `focus_sound.words`，脚本会用 CMU 英语发音词典逐词核对例词确实含这个音（two 不含 /θ/，会被拦下）。一份报告只有一个重点音，老师说、小目标、在家练都说这一个。

挑重点的顺序：影响听懂的程度（被听成别的词 > 只是不够标准）> 出现次数 > 是否本课核心词。

| 键 | 名称 | 常被发成 | 纠音说法 | 对比词 | 在家练 |
|----|------|---------|---------|--------|--------|
| `θ` | th 清音（three、mouth） | s、f | 舌尖轻放在上下门牙之间，轻轻吹气 | three / free，mouth / mouse | 对着镜子说，能看到一点舌尖就对了 |
| `ð` | th 浊音（this、mother） | d、z | 舌尖轻放在上下门牙之间，同时让喉咙振动 | then / den，they / day | 手摸喉咙说 this，感到振动就对了 |
| `v` | v（very、oval） | w、f | 上门牙轻碰下嘴唇，送气时喉咙振动 | vest / west，van / fan | 手摸喉咙，嘴唇被上门牙轻轻碰着发音 |
| `w` | w（water、window） | v | 双唇收圆向前，再快速张开，牙齿不碰嘴唇 | wet / vet，wine / vine | 像吹蜡烛一样收圆嘴唇再说 |
| `r` | r（red、run） | l、w | 舌尖向上翘起但不碰上颚，嘴唇微微收圆 | right / light，red / led | 先拉长 rrr 再接元音 |
| `l` | l 词首（lake、leg） | n、r | 舌尖抵住上门牙后面的牙床，声音从舌头两边出来 | light / right，lake / rake | 舌尖抵住牙床停一秒再说 |
| `词尾l` | 词尾 l（ball、school） | 被省掉或发成「哦」 | 词尾也要把舌尖抬起抵住上牙床，再收住 | tall / toe，bowl / bow | 说完词停住，检查舌尖是否抬起 |
| `n-ŋ` | n 与 ng（sun、sing） | 两者混用 | n 舌尖抵上牙床；ng 舌根抬起，舌尖放下 | sin / sing，ran / rang | 先慢说 sin，再说 sing，比较舌头位置 |
| `n-l` | n 与 l（night、light） | 两者混用 | n 的气从鼻子出，捏住鼻子就发不出；l 的气从舌头两边出 | night / light，no / low | 捏住鼻子分别试说两个词 |
| `ʃ` | sh（ship、fish） | s、汉语 x | 嘴唇向前撅起，舌头抬高靠近上颚，送气 | ship / sip，she / see | 做「嘘」的嘴型再说 |
| `z` | z（zoo、nose） | s | 像小蜜蜂嗡嗡叫，摸喉咙能感到振动 | zoo / sue，eyes / ice | 先拉长 zzz 再接词 |
| `tʃ-dʒ` | ch 与 j（chair、juice） | 汉语 q、j | 嘴唇撅起，舌尖先抵住上牙床，再突然放开 | chair / share，jeep / cheap | 先撅嘴，再弹开舌尖 |
| `h` | h（hat、hello） | 喉咙摩擦重的汉语 h | 轻轻哈一口气，像对着玻璃哈气，喉咙不用力 | hat / at，hill / ill | 对着手心轻轻哈气再说 |
| `词尾辅音` | 词尾辅音（bed、eight） | 被吞掉 | 词尾的音要做出口型、轻轻收住，不加额外的音 | bead / bee，card / car | 拍手说词，最后一个音落在拍子上 |
| `词尾加音` | 词尾多加一个音（dog 说成 dog-e） | 词尾带出「额」 | 词尾的音要做出口型、轻轻收住，不加额外的音 | sit / city，bag / baggy | 说完马上闭嘴，不让声音拖出来 |
| `辅音连缀` | 辅音连缀（tree、play） | 中间插「额」或丢一个 | 两个辅音紧挨着发，中间不插「额」 | play / pay，tree / tea | 先慢后快，把两个辅音连成一下 |
| `词尾s` | 词尾 s、z（monkeys、cats） | 被省掉 | 词尾轻轻带出「丝」或「滋」的气流，不吞掉 | cat / cats，monkey / monkeys | 说复数时用手指比一个「多」 |
| `iː-ɪ` | 长短 i（sheep、ship） | 读成一样 | 长音 ee 嘴角向两边拉开、拉长；短音 i 放松、短促 | sheep / ship，seat / sit | 长音拍两下，短音拍一下 |
| `æ` | a（cat、apple） | e、a | 嘴巴张大，嘴角向两边拉，舌尖抵住下门牙 | bad / bed，man / men | 照镜子看嘴巴张够大没有 |
| `ʌ` | u（cup、bus） | a、o | 嘴巴自然半张，短促地发「啊」 | cup / cap，bus / boss | 短促地说，像被吓了一下 |
| `ɜː` | er（bird、girl） | e、带卷舌 | 嘴巴半张、舌头放平，拉长「额」，不卷舌 | bird / bud，word / wad | 拉长音时舌头保持不动 |
| `ʊ-uː` | 长短 oo（pool、pull） | 读成一样 | 长音 oo 嘴唇收圆拉长；短音 oo 放松、短促 | pool / pull，fool / full | 长音拍两下，短音拍一下 |
| `a-e` | magic e：a-e（cake、lake） | 短音 a | 读字母 A 本身的音，从「诶」滑到「衣」 | cap / cape，mad / made | 盖住 e 读一遍，露出 e 再读一遍 |
| `i-e` | magic e：i-e（bike、kite） | 短音 i | 读字母 I 本身的音，从「啊」滑到「衣」 | kit / kite，pin / pine | 盖住 e 读一遍，露出 e 再读一遍 |
| `o-e` | magic e：o-e（stone、home） | 短音 o | 读字母 O 本身的音，嘴唇从圆到更圆，最后收拢 | hop / hope，not / note | 盖住 e 读一遍，露出 e 再读一遍 |
| `u-e` | magic e：u-e（mule、cube） | 「衣」长音、短音 u | 读字母 U 本身的音，先「衣」再滑到「乌」，嘴唇收圆向前 | cub / cube，us / use | 盖住 e 读一遍，露出 e 再读一遍 |
| `重音` | 双音节词重音（salad、yellow） | 重音放错或平均用力 | 重读的音节说得更响、更长、音调更高 | YEL-low，SAL-ad | 重读的音节拍一下手 |

只收常见难点；新增一行时，同时在 `scripts/coach.py` 的 `PATTERNS` 里写上它在 CMU 词典里怎么核对。
