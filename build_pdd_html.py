# -*- coding: utf-8 -*-
"""Собирает pdd.html из pdd-armenia-ru.md + иллюстраций из illustrations/.

Иллюстрация вставляется СРАЗУ ПОСЛЕ блока пункта с номером-ключом из FIGURES
(включая его подпункты; нумерация пунктов сквозная, поэтому ключ однозначен).
Добавить картинку к другой главе: положить svg в illustrations/ и дописать
строку в FIGURES.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "pdd-armenia-ru.md"
OUT = ROOT / "pdd.html"
ILL = ROOT / "illustrations"

# после какого пункта вставить: (файл, подпись)
FIGURES = {
    3: ("ch1-p3.svg",
        "Опережение — обошёл соседа по попутной полосе, на встречную не выезжал. "
        "Обгон — только манёвр с выездом на полосу встречного движения. В билетах их путают специально."),
    10: ("ch2-p10.svg",
         "Горит стрелка доп. секции — в её направлении ехать можно, даже при красном основном "
         "(но приоритета она не даёт). Секция погасла — в её направлении нельзя, даже на зелёный: "
         "контурная стрелка на основном зелёном как раз предупреждает об этом."),
    16: ("ch2-p16.svg",
         "Два главных положения регулировщика. Руки опущены или в стороны: ехать можно только "
         "с боков — прямо и направо. Правая рука вперёд: с левого бока — в любую сторону, "
         "со стороны груди — только направо, правому боку и спине — стоп. "
         "Запоминалка: открытые «ворота» из рук — можно, грудь и спина — стена."),
    23: ("ch3-p23.svg",
         "Аварийка включается сразу, знак (или красный мигающий фонарик) выставляется "
         "не ближе 15 м от машины в населённом пункте и 30 м вне его — навстречу потоку."),
    28: ("ch4-p28.svg",
         "Синий маячок + сирена: уступи дорогу любым способом — освободи полосу, прими вправо, "
         "остановись. К стоящей машине с синим или красным маячком подъезжай, заранее снизив "
         "скорость (пп. 28–31)."),
    38: ("ch5-p38.svg",
         "Выезд с прилегающей территории (двор, парковка, АЗС): уступаешь всем на дороге — "
         "и машинам, и пешеходам. Ты здесь последний в очереди."),
    39: ("ch5-p39.svg",
         "Слева — обычное перестроение: уступает тот, кто манёврит. "
         "Справа — перестраиваются оба одновременно: уступает тот, кто левее."),
    40: ("ch5-p40.svg",
         "По умолчанию налево — только из крайнего левого ряда. Если стрелки на асфальте "
         "(разметка 1.18) или знак разрешают — можно из нескольких рядов: это исключение 2."),
    41: ("ch5-p41.svg",
         "Разрешена только зелёная траектория: на выезде с перекрёстка ты на своей половине. "
         "Красная срезает угол и проходит по встречной — даже пустой это грубая ошибка."),
    42: ("ch5-p42.svg",
         "Поворот на дорогу с реверсивной полосой (двойная прерывистая разметка): "
         "сначала — в крайнюю правую. В реверсивную — только убедившись по светофорам "
         "над ней, что она открыта в твою сторону."),
    44: ("ch5-p44.svg",
         "Разворот вне перекрёстка разрешён, но уступи всем встречным "
         "(и попутному трамваю, если пути слева)."),
    45: ("ch5-p45.svg",
         "Знаков нет, дороги равные, траектории пересекаются: уступает тот, к кому машина "
         "приближается справа. «Кто справа — тот и прав»."),
    46: ("ch5-p46.svg",
         "Препятствие на твоей полосе — объезжаешь через встречку, значит уступаешь ты. "
         "На крутом уклоне (знаки 1.13/1.14) наоборот: уступает тот, кто едет на спуск."),
    47: ("ch5-p47.svg",
         "Есть полоса торможения — перестройся в неё заранее и снижай скорость уже там, "
         "а не в общем потоке."),
    50: ("ch5-p50.svg",
         "Пять из семи мест, где запрещён разворот. Ещё два не нарисуешь: видимость дороги "
         "менее 100 м и односторонние дороги."),
    53: ("ch6-p53.svg",
         "Дорога 2+2 полосы и шире: встречная сторона закрыта полностью — обгоняй и объезжай "
         "только в пределах своих полос. Середину такой дороги обычно отмечает двойная сплошная."),
    54: ("ch6-p54.svg",
         "Трёхполосная двусторонняя: средняя полоса общая — на неё можно для обгона, объезда, "
         "поворота налево и разворота. Крайняя левая принадлежит встречным целиком. "
         "Это правило по умолчанию: знак 5.15.7 или разметка могут закрепить полосы иначе — тогда действуют они."),
    57: ("ch6-p57.svg",
         "Три и более полос в твою сторону: крайняя левая — только при заторе в остальных "
         "или для поворота налево/разворота (грузовикам от 3,5 т — только для поворота/разворота). "
         "Базовый принцип: держись правее."),
    62: ("ch6-p62.svg",
         "Дистанция и боковой интервал — на твоей ответственности: конкретных метров правила "
         "не называют. Врезался сзади — почти всегда виноват тот, кто не держал дистанцию."),
    64: ("ch6-p64.svg",
         "Островок безопасности, тумба, опора моста посередине дороги — объезжай справа "
         "(препятствие остаётся слева от тебя). Слева — значит по встречке. "
         "Знаки или разметка могут предписать иное."),
    69: ("ch7-p69.svg",
         "Четыре базовых лимита для легковушки: 20 — жилая зона и дворы, 60 — населённый пункт, "
         "90 — вне его, 110 — автомагистраль. Всё остальное в билетах — поправки к этой шкале "
         "для грузовиков, автобусов, прицепов и буксировки."),
    74: ("ch8-p74.svg",
         "Обгон — только слева. Единственное исключение: впереди идущий включил левый поворотник "
         "и начал манёвр — тогда его объезжают справа."),
    77: ("ch8-p77.svg",
         "Места запрета обгона из п. 77: перекрёстки, переходы, переезды и 100 м перед ними, "
         "мосты и тоннели, конец подъёма. Плюс нельзя обгонять того, кто сам обгоняет, "
         "и машины с синими маячками."),
    84: ("ch9-p84.svg",
         "Три самых экзаменационных метража: 5 м до пешеходного перехода (за ним — можно), "
         "15 м от остановки в обе стороны, 3 м свободного пространства до сплошной или "
         "противоположного края. Для стоянки добавь: 50 м от переезда и запрет на главной вне города."),
    90: ("ch10-p90.svg",
         "Зелёный разрешает движение и тебе, и встречному. Поворачивая налево, ты пересекаешь "
         "его траекторию — уступи всем встречным, едущим прямо и направо, и только потом заверши манёвр."),
    96: ("ch10-p96.svg",
         "Знак 2.1 — ты на главной, едешь первым. Знак 2.4 — уступи всем на пересекаемой дороге, "
         "независимо от того, куда они поворачивают. Не видно покрытия (ночь, снег) и знаков нет — "
         "считай себя на второстепенной (п. 101)."),
    98: ("ch10-p98.svg",
         "Равнозначный перекрёсток: правило одно — «помеха справа». Кто приближается к тебе справа, "
         "тот проезжает первым. Трамвай на таких перекрёстках всегда в приоритете."),
    104: ("ch11-p104.svg",
          "Машина в соседнем ряду остановилась или притормозила перед переходом — это сигнал: "
          "там пешеход, которого ты не видишь. Продолжать можно только убедившись, что перед ней никого нет."),
    111: ("ch12-p111.svg",
          "Переезд закрыт — стой у стоп-линии или знака 2.5; их нет — за 5 м до шлагбаума; "
          "нет и шлагбаума — за 10 м до ближайшего рельса. Объезжать стоящих перед переездом "
          "по встречке и открывать шлагбаум самому — запрещено."),
    116: ("ch13-p116.svg",
          "Автомагистраль (знак 5.1): скоростная дорога без пересечений. Запрещены развороты "
          "и въезд в разрывы разделительной полосы, задний ход, остановка вне площадок, пешеходы, "
          "учебная езда и всё, что едет медленнее 40 км/ч."),
    124: ("ch15-p124.svg",
          "По полосе «А» ездить и стоять нельзя. Но если она отделена прерывистой линией — "
          "перед поворотом направо перестроиться на неё обязательно; можно заезжать при въезде "
          "на дорогу и для посадки-высадки у правого края, не мешая автобусам."),
    128: ("ch16-p128.svg",
          "Дальний свет слепит встречных: переключайся на ближний минимум за 150 м, в освещённом "
          "городе — всегда. Ослепили тебя — не дёргай руль: аварийка, плавно тормози в своей полосе."),
    140: ("ch17-p140.svg",
          "Числа для билетов: трос 4–6 м, жёсткая сцепка до 4 м, скорость до 50 км/ч, "
          "на тросе минимум два сигнальных флажка. В гололёд на тросе — нельзя."),
    162: ("ch20-p162.svg",
          "Габариты груза без спецобозначений: до 1 м сзади и спереди, до 0,4 м сбоку. "
          "Больше — знак «Крупногабаритный груз», ночью плюс фонари: белый вперёд, красный назад."),
}

# ── мини-пиктограммы знаков ──────────────────────────────────────────────
# После пункта, где в тексте упомянуты знаки/разметка с номерами,
# автоматически вставляется полоска .signs с картинками и названиями.
RED, BLUE, GREEN, YEL = "#d23b3b", "#2266bb", "#2e7d4f", "#f4c73f"
W, BK, GRAY = "#fff", "#333", "#8a8a8a"

SIGNS_DIR = ILL / "signs"   # официальные SVG знаков (Wikimedia Commons, ГОСТ)
_sign_cache = {}


def official_sign(num):
    """Инлайн официального знака: чистка мусора, viewBox, изоляция id."""
    if num in _sign_cache:
        return _sign_cache[num]
    s = (SIGNS_DIR / f"{num}.svg").read_text(encoding="utf-8")
    for pat in (r"<\?xml.*?\?>", r"<!--.*?-->", r"<!DOCTYPE.*?>",
                r"<metadata.*?</metadata>", r"<sodipodi:namedview.*?(?:/>|</sodipodi:namedview>)"):
        s = re.sub(pat, "", s, flags=re.S)
    m = re.search(r"<svg[^>]*>", s, re.S)
    tag = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', tag)
    if vb:
        viewbox = vb.group(1)
    else:
        w = re.search(r'width="([\d.]+)', tag).group(1)
        h = re.search(r'height="([\d.]+)', tag).group(1)
        viewbox = f"0 0 {w} {h}"
    body = s[m.end():s.rindex("</svg>")]
    pref = "s" + num.replace(".", "") + "_"
    for i in set(re.findall(r'\bid="([^"]+)"', body)):
        body = body.replace(f'id="{i}"', f'id="{pref}{i}"')
        body = body.replace(f"url(#{i})", f"url(#{pref}{i})")
        body = body.replace(f'href="#{i}"', f'href="#{pref}{i}"')
    out = f'<svg viewBox="{viewbox}" aria-hidden="true">{body}</svg>'
    _sign_cache[num] = out
    return out


_SIGN_PLACEHOLDER = re.compile(r"<!--SIGN:([\d.]+):(-?\d+):(-?\d+):(\d+)-->")


def expand_scene_signs(svg):
    """Заменить в сюжетной схеме плейсхолдеры <!--SIGN:номер:x:y:ширина--> официальными знаками."""
    def rep(m):
        num, x, y, w = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        inner = official_sign(num)
        vb = re.search(r'viewBox="([^"]+)"', inner).group(1).split()
        h = round(w * float(vb[3]) / float(vb[2]))
        return inner.replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h}" ', 1)
    return _SIGN_PLACEHOLDER.sub(rep, svg)


def _circ(inner):
    return f'<circle cx="32" cy="32" r="27" fill="{W}" stroke="{RED}" stroke-width="6"/>{inner}'


def _tri(inner):
    return (f'<path d="M32 6 L60 56 L4 56 Z" fill="{W}" stroke="{RED}" '
            f'stroke-width="5" stroke-linejoin="round"/>{inner}')


def _sq(color, inner):
    return f'<rect x="4" y="4" width="56" height="56" rx="7" fill="{color}"/>{inner}'


def _uparrow(x, color=W, w=3.5):
    return (f'<path d="M{x} 52 V16 M{x} 16 L{x-5} 24 M{x} 16 L{x+5} 24" '
            f'stroke="{color}" stroke-width="{w}" fill="none"/>')


def _downarrow(x, color=W, w=3.5):
    return (f'<path d="M{x} 12 V48 M{x} 48 L{x-5} 40 M{x} 48 L{x+5} 40" '
            f'stroke="{color}" stroke-width="{w}" fill="none"/>')


_BUS = (f'<rect x="16" y="18" width="32" height="20" rx="4" fill="{W}"/>'
        f'<rect x="20" y="22" width="7" height="7" fill="{BLUE}"/>'
        f'<rect x="30" y="22" width="7" height="7" fill="{BLUE}"/>'
        f'<rect x="40" y="22" width="5" height="7" fill="{BLUE}"/>'
        f'<circle cx="23" cy="42" r="4" fill="{W}"/><circle cx="41" cy="42" r="4" fill="{W}"/>')

_HIGHWAY = (f'<rect x="20" y="34" width="6" height="18" fill="{W}"/>'
            f'<rect x="38" y="34" width="6" height="18" fill="{W}"/>'
            f'<rect x="14" y="26" width="36" height="6" fill="{W}"/>'
            f'<line x1="23" y1="10" x2="23" y2="22" stroke="{W}" stroke-width="4" stroke-dasharray="5 4"/>'
            f'<line x1="41" y1="10" x2="41" y2="22" stroke="{W}" stroke-width="4" stroke-dasharray="5 4"/>')

_ZONE = (f'<path d="M14 30 L26 20 L38 30 Z" fill="{W}"/><rect x="18" y="30" width="16" height="14" fill="{W}"/>'
         f'<circle cx="46" cy="26" r="3.5" fill="{W}"/>'
         f'<path d="M46 30 V40 M46 33 L41 38 M46 33 L51 38" stroke="{W}" stroke-width="2" fill="none"/>'
         f'<rect x="38" y="44" width="14" height="7" rx="2" fill="{W}"/>')

_DIAMOND = (f'<rect x="11" y="11" width="42" height="42" rx="5" transform="rotate(45 32 32)" '
            f'fill="{W}" stroke="{GRAY}" stroke-width="2"/>'
            f'<rect x="21" y="21" width="22" height="22" rx="3" transform="rotate(45 32 32)" fill="{YEL}"/>')

_SLASH = f'<line x1="10" y1="54" x2="54" y2="10" stroke="{RED}" stroke-width="6"/>'

_ASPHALT = f'<rect x="4" y="4" width="56" height="56" rx="6" fill="#4a4a48"/>'

# номер: (название, содержимое svg 64×64)
SIGN_DEFS = {
    "1.13": ("Знак 1.13 «Крутой спуск»", _tri(f'<path d="M16 51 L48 51 L16 39 Z" fill="{BK}"/>')),
    "1.14": ("Знак 1.14 «Крутой подъём»", _tri(f'<path d="M16 51 L48 51 L48 39 Z" fill="{BK}"/>')),
    "2.1": ("Знак 2.1 «Главная дорога»", _DIAMOND),
    "2.2": ("Знак 2.2 «Конец главной дороги»", _DIAMOND + f'<line x1="14" y1="50" x2="50" y2="14" stroke="{BK}" stroke-width="5"/>'),
    "2.3.1": ("Знак 2.3.1 «Пересечение со второстепенной дорогой»",
              _tri(f'<line x1="32" y1="18" x2="32" y2="50" stroke="{BK}" stroke-width="6"/>'
                   f'<line x1="18" y1="38" x2="46" y2="38" stroke="{BK}" stroke-width="3"/>')),
    "2.3.2": ("Знаки 2.3.2–2.3.7 «Примыкание второстепенной дороги»",
              _tri(f'<line x1="32" y1="18" x2="32" y2="50" stroke="{BK}" stroke-width="6"/>'
                   f'<line x1="32" y1="38" x2="46" y2="38" stroke="{BK}" stroke-width="3"/>')),
    "2.4": ("Знак 2.4 «Уступите дорогу»",
            f'<path d="M6 10 L58 10 L32 56 Z" fill="{W}" stroke="{RED}" stroke-width="5" stroke-linejoin="round"/>'),
    "2.5": ("Знак 2.5 «Движение без остановки запрещено»",
            f'<path d="M20 4 L44 4 L60 20 L60 44 L44 60 L20 60 L4 44 L4 20 Z" fill="{RED}" stroke="{W}" stroke-width="3"/>'
            f'<text x="32" y="37" font-size="13" font-weight="700" fill="{W}" text-anchor="middle">STOP</text>'),
    "2.6": ("Знак 2.6 «Преимущество встречного движения»",
            _circ(_downarrow(23, BK, 4) + _uparrow(41, RED, 4).replace('52 V16', '50 V18'))),
    "3.11": ("Знак 3.11 «Ограничение массы»",
             _circ(f'<text x="32" y="40" font-size="19" font-weight="700" fill="{BK}" text-anchor="middle">5т</text>')),
    "3.12": ("Знак 3.12 «Ограничение массы на ось»",
             _circ(f'<text x="32" y="31" font-size="14" font-weight="700" fill="{BK}" text-anchor="middle">3т</text>'
                   f'<line x1="18" y1="40" x2="46" y2="40" stroke="{BK}" stroke-width="4"/>'
                   f'<circle cx="23" cy="46" r="4" fill="{BK}"/><circle cx="41" cy="46" r="4" fill="{BK}"/>')),
    "3.13": ("Знак 3.13 «Ограничение высоты»",
             _circ(f'<text x="32" y="38" font-size="13" font-weight="700" fill="{BK}" text-anchor="middle">3,5м</text>'
                   f'<path d="M32 12 L27 20 H37 Z" fill="{RED}"/><path d="M32 52 L27 44 H37 Z" fill="{RED}"/>')),
    "3.14": ("Знак 3.14 «Ограничение ширины»",
             _circ(f'<text x="32" y="38" font-size="13" font-weight="700" fill="{BK}" text-anchor="middle">2,2м</text>'
                   f'<path d="M12 32 L20 27 V37 Z" fill="{RED}"/><path d="M52 32 L44 27 V37 Z" fill="{RED}"/>')),
    "3.17.2": ("Знак 3.17.2 «Опасность»",
               _circ(f'<text x="32" y="43" font-size="30" font-weight="700" fill="{BK}" text-anchor="middle">!</text>')),
    "3.20": ("Знак 3.20 «Обгон запрещён»",
             _circ(f'<rect x="11" y="26" width="18" height="12" rx="2" fill="{RED}"/>'
                   f'<rect x="35" y="26" width="18" height="12" rx="2" fill="{BK}"/>')),
    "3.24": ("Знак 3.24 «Ограничение максимальной скорости»",
             _circ(f'<text x="32" y="41" font-size="21" font-weight="700" fill="{BK}" text-anchor="middle">60</text>')),
    "5.1": ("Знак 5.1 «Автомагистраль»", _sq(GREEN, _HIGHWAY)),
    "5.2": ("Знак 5.2 «Конец автомагистрали»", _sq(GREEN, _HIGHWAY) + _SLASH),
    "5.3": ("Знак 5.3 «Дорога для автомобилей»",
            _sq(BLUE, f'<rect x="20" y="16" width="24" height="12" rx="4" fill="{W}"/>'
                      f'<rect x="14" y="24" width="36" height="20" rx="6" fill="{W}"/>'
                      f'<circle cx="22" cy="47" r="5" fill="{BLUE}" stroke="{W}" stroke-width="3"/>'
                      f'<circle cx="42" cy="47" r="5" fill="{BLUE}" stroke="{W}" stroke-width="3"/>')),
    "5.11": ("Знак 5.11 «Дорога с полосой для маршрутных ТС»",
             _sq(BLUE, _uparrow(18) +
                 f'<rect x="34" y="18" width="18" height="12" rx="2" fill="{W}"/>'
                 f'<path d="M43 36 V50 M43 50 L38 44 M43 50 L48 44" stroke="{W}" stroke-width="3.5" fill="none"/>')),
    "5.13.1": ("Знак 5.13.1 «Выезд на дорогу с полосой для маршрутных ТС»",
               _sq(BLUE, f'<rect x="12" y="18" width="17" height="11" rx="2" fill="{W}"/>'
                         f'<path d="M16 46 H48 M40 39 L48 46 L40 53" stroke="{W}" stroke-width="4" fill="none"/>')),
    "5.13.2": ("Знак 5.13.2 «Выезд на дорогу с полосой для маршрутных ТС»",
               _sq(BLUE, f'<rect x="35" y="18" width="17" height="11" rx="2" fill="{W}"/>'
                         f'<path d="M48 46 H16 M24 39 L16 46 L24 53" stroke="{W}" stroke-width="4" fill="none"/>')),
    "5.14": ("Знак 5.14 «Полоса для маршрутных ТС»", _sq(BLUE, _BUS)),
    "5.15.1": ("Знак 5.15.1 «Направления движения по полосам»",
               _sq(BLUE, f'<line x1="24" y1="8" x2="24" y2="56" stroke="{W}" stroke-width="1.5"/>'
                         f'<line x1="43" y1="8" x2="43" y2="56" stroke="{W}" stroke-width="1.5"/>'
                         f'<path d="M14 52 V26 Q14 19 8 19" stroke="{W}" stroke-width="3.5" fill="none"/>'
                         f'<path d="M6 19 L15 14 L14 24 Z" fill="{W}"/>' + _uparrow(33) + _uparrow(52))),
    "5.15.2": ("Знак 5.15.2 «Направления движения по полосе»", _sq(BLUE, _uparrow(32, W, 4.5))),
    "5.15.7": ("Знак 5.15.7 «Направление движения по полосам»",
               _sq(BLUE, f'<line x1="24" y1="8" x2="24" y2="56" stroke="{W}" stroke-width="1.5"/>'
                         f'<line x1="43" y1="8" x2="43" y2="56" stroke="{W}" stroke-width="1.5"/>' +
                         _downarrow(14) + _uparrow(33) + _uparrow(52))),
    "5.15.8": ("Знак 5.15.8 «Число полос»",
               _sq(BLUE, f'<text x="32" y="26" font-size="17" font-weight="700" fill="{W}" text-anchor="middle">3</text>'
                         f'<path d="M18 54 V36 M18 36 L14 42 M18 36 L22 42" stroke="{W}" stroke-width="3" fill="none"/>'
                         f'<path d="M32 54 V36 M32 36 L28 42 M32 36 L36 42" stroke="{W}" stroke-width="3" fill="none"/>'
                         f'<path d="M46 54 V36 M46 36 L42 42 M46 36 L50 42" stroke="{W}" stroke-width="3" fill="none"/>')),
    "5.21": ("Знак 5.21 «Жилая зона»", _sq(BLUE, _ZONE)),
    "5.22": ("Знак 5.22 «Конец жилой зоны»", _sq(BLUE, _ZONE) + _SLASH),
    "6.4": ("Знак 6.4 «Место стоянки»",
            _sq(BLUE, f'<text x="32" y="47" font-size="38" font-weight="700" fill="{W}" text-anchor="middle">P</text>')),
    "6.16": ("Знак 6.16 «Стоп-линия»",
             f'<rect x="4" y="16" width="56" height="32" rx="4" fill="{W}" stroke="{GRAY}" stroke-width="2"/>'
             f'<text x="32" y="42" font-size="15" font-weight="700" fill="{BK}" text-anchor="middle">СТОП</text>'),
    "7.11": ("Знак 7.11 «Место отдыха»",
             _sq(BLUE, f'<rect x="10" y="10" width="44" height="44" rx="4" fill="{W}"/>'
                       f'<path d="M22 42 L32 22 L42 42 Z" fill="{GREEN}"/>'
                       f'<rect x="30" y="42" width="4" height="8" fill="{BK}"/>')),
    "8.6.2": ("Табличка 8.6.2 «Способ постановки на стоянку»",
              f'<rect x="4" y="10" width="56" height="44" rx="4" fill="{W}" stroke="{GRAY}" stroke-width="2"/>'
              f'<line x1="8" y1="44" x2="56" y2="44" stroke="{BK}" stroke-width="3"/>'
              f'<rect x="21" y="38" width="22" height="11" rx="2" fill="none" stroke="{BK}" stroke-width="2.5"/>'),
    "8.6.3": ("Табличка 8.6.3 «Способ постановки на стоянку»",
              f'<rect x="4" y="10" width="56" height="44" rx="4" fill="{W}" stroke="{GRAY}" stroke-width="2"/>'
              f'<line x1="8" y1="44" x2="56" y2="44" stroke="{BK}" stroke-width="3"/>'
              f'<rect x="26" y="24" width="12" height="24" rx="2" fill="none" stroke="{BK}" stroke-width="2.5"/>'),
    "8.6.6": ("Таблички 8.6.6–8.6.9 «Способ постановки на стоянку»",
              f'<rect x="4" y="10" width="56" height="44" rx="4" fill="{W}" stroke="{GRAY}" stroke-width="2"/>'
              f'<line x1="8" y1="44" x2="56" y2="44" stroke="{BK}" stroke-width="3"/>'
              f'<rect x="21" y="26" width="22" height="11" rx="2" fill="none" stroke="{BK}" stroke-width="2.5"/>'),
    "1.9": ("Разметка 1.9 — границы реверсивной полосы (двойная прерывистая)",
            _ASPHALT + f'<line x1="24" y1="8" x2="24" y2="56" stroke="{W}" stroke-width="4" stroke-dasharray="9 7"/>'
                       f'<line x1="38" y1="8" x2="38" y2="56" stroke="{W}" stroke-width="4" stroke-dasharray="9 7"/>'),
    "1.12": ("Разметка 1.12 «Стоп-линия»", _ASPHALT + f'<rect x="10" y="38" width="44" height="8" fill="{W}"/>'),
    "1.17": ("Разметка 1.17 — место остановки маршрутных ТС (в Армении красная)",
             _ASPHALT + f'<polyline points="8,36 16,28 24,36 32,28 40,36 48,28 56,36" fill="none" stroke="{RED}" stroke-width="3.5"/>'),
    "1.18": ("Разметка 1.18 — направления движения по полосам (стрелы)",
             _ASPHALT + f'<path d="M20 52 V24 M20 24 L14 32 M20 24 L26 32" stroke="{W}" stroke-width="4" fill="none"/>'
                        f'<path d="M44 52 V32 Q44 24 36 24" stroke="{W}" stroke-width="4" fill="none"/>'
                        f'<path d="M34 24 L44 19 L43 30 Z" fill="{W}"/>'),
    "1.4": ("Разметка 1.4 (жёлтая) — остановка запрещена",
            _ASPHALT + f'<line x1="12" y1="8" x2="12" y2="56" stroke="{YEL}" stroke-width="5"/>'),
    "1.10": ("Разметка 1.10 (жёлтая) — стоянка запрещена",
             _ASPHALT + f'<line x1="12" y1="8" x2="12" y2="56" stroke="{YEL}" stroke-width="5" stroke-dasharray="8 7"/>'),
    "1.14.1": ("Разметка 1.14.1 «Пешеходный переход» (жёлто-белая «зебра»)",
               _ASPHALT + f'<rect x="12" y="10" width="8" height="44" fill="{YEL}"/>'
                          f'<rect x="28" y="10" width="8" height="44" fill="{W}"/>'
                          f'<rect x="44" y="10" width="8" height="44" fill="{YEL}"/>'),
}
# где есть официальный файл — он вытесняет рисованный глиф
for _n in list(SIGN_DEFS):
    if (SIGNS_DIR / f"{_n}.svg").exists():
        SIGN_DEFS[_n] = (SIGN_DEFS[_n][0], official_sign(_n))
SIGN_DEFS["8.6.9"] = SIGN_DEFS["8.6.6"]
SIGN_DEFS["1.14.2"] = SIGN_DEFS["1.14.1"]
SIGN_DEFS["2.3.7"] = SIGN_DEFS["2.3.2"]

_SIGN_WORD = re.compile(r"знак|таблич|разметк|лини", re.I)
_SIGN_NUM = re.compile(r"\d+\.\d+(?:\.\d+)?")


def signs_strip(text):
    """Полоска пиктограмм для знаков/разметки, упомянутых в тексте пункта."""
    if not _SIGN_WORD.search(text):
        return None
    items, seen = [], set()
    for num in _SIGN_NUM.findall(text):
        entry = SIGN_DEFS.get(num)
        if not entry or entry[0] in seen:
            continue
        seen.add(entry[0])
        name, glyph = entry
        if not glyph.startswith("<svg"):
            glyph = f'<svg viewBox="0 0 64 64" aria-hidden="true">{glyph}</svg>'
        items.append(f'<div class="sign">{glyph}<span>{name}</span></div>')
    if not items:
        return None
    return f'<div class="signs">{"".join(items)}</div>'


CSS = """
:root{--bg:#faf9f5;--fg:#2c2c2a;--muted:#807e76;--card:#fff;--border:#e3e1d9;
--road:#efede6;--roadline:#d8d5cb;--lane:#b9b7ae;--paint:#fff;
--ok:#3b6d11;--bad:#a32d2d;--warn:#ba7517;--accent:#0f6e56;
--carfill:#b5d4f4;--carstroke:#185fa5;--car2fill:#f5c4b3;--car2stroke:#993c1d}
@media (prefers-color-scheme: dark){
:root{--bg:#1f1e1c;--fg:#e8e6e1;--muted:#98968e;--card:#292825;--border:#3c3b37;
--road:#383733;--roadline:#4a4944;--lane:#75736b;--paint:#d5d3cc;
--ok:#97c459;--bad:#f09595;--warn:#fac775;--accent:#5dcaa5;
--carfill:#0c447c;--carstroke:#85b7eb;--car2fill:#712b13;--car2stroke:#f0997b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.7 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.layout{display:block}
.burger{position:fixed;top:12px;left:12px;z-index:20;background:var(--card);
color:var(--fg);border:1px solid var(--border);border-radius:10px;
padding:9px 14px;font-size:15px;font-family:inherit;cursor:pointer}
aside{display:none}
body.navopen aside{display:block;position:fixed;inset:0;z-index:15;overflow-y:auto;
background:var(--bg);padding:64px 20px 40px;font-size:15px}
body.navopen{overflow:hidden}
aside .brand{font-weight:600;margin-bottom:8px}
aside a{display:block;color:var(--fg);text-decoration:none;padding:6px 8px;
border-radius:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
aside a:hover{background:var(--card);color:var(--accent)}
aside a.active{background:var(--card);color:var(--accent);font-weight:600}
main{max-width:800px;margin:0 auto;padding:60px 20px 80px;min-width:0}
@media (min-width:1100px){
.burger{display:none}
.layout{display:grid;grid-template-columns:280px minmax(0,1fr)}
aside{display:block;position:sticky;top:0;height:100vh;overflow-y:auto;
border-right:1px solid var(--border);padding:24px 16px;font-size:14px}
aside a{padding:3px 8px}
main{padding-top:24px}}
h1{font-size:25px;line-height:1.3;margin:8px 0}
h2{font-size:20px;margin:52px 0 12px;padding-top:18px;border-top:1px solid var(--border)}
.intro{color:var(--muted);font-size:14px;border-left:3px solid var(--border);
padding-left:12px;margin:14px 0 26px}
p{margin:10px 0}
p.sub{margin-left:26px}
.num{font-weight:600;color:var(--accent)}
figure{background:var(--card);border:1px solid var(--border);border-radius:14px;
padding:20px 20px 8px;margin:24px 0}
figure svg{display:block;max-width:100%;height:auto}
figcaption{font-size:14px;color:var(--muted);padding:10px 4px 10px;line-height:1.55;
border-top:1px solid var(--border);margin-top:12px}
.signs{display:flex;flex-wrap:wrap;align-items:flex-start;gap:14px 22px;background:var(--card);
border:1px solid var(--border);border-radius:14px;padding:14px 16px;margin:18px 0}
.sign{max-width:210px;min-width:100px;display:flex;flex-direction:column;
align-items:center;text-align:center}
.sign svg{height:72px;width:auto;max-width:210px;display:block}
.sign span{font-size:11px;color:var(--muted);line-height:1.35;margin-top:6px}
a.pref{color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent)}
a.pref:hover{border-bottom-style:solid}
"""


def slug_chapter(title):
    m = re.match(r"(\d+)\.", title)
    return f"g{m.group(1)}" if m else "g0"


def short_title(title):
    return re.sub(r"^(\d+)\.\s*", r"\1. ", title)


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


MAX_POINT = 175
_NUM = r"\d+(?!\.\d)(?<!\.\d\d)(?<!\.\d)"
_NUMRANGE = rf"{_NUM}(?:\s*[-–—]\s*{_NUM})?"
_NUMLIST = rf"{_NUMRANGE}(?:\s*(?:,\s*|,?\s*и\s*){_NUMRANGE})*"


def _plink(numstr):
    def one(d):
        n = int(d.group(0))
        return f'<a class="pref" href="#p{n}">{n}</a>' if 1 <= n <= MAX_POINT else d.group(0)
    return re.sub(r"\d+", one, numstr)


def link_points(t):
    """«пункт N» → якорная ссылка на #pN. «пункта X пункта Y» — ссылка только на Y."""
    # вложенные: «пункта 2 пункта 33», «пунктам 5 и 6 пункта 143» — X это подпункты
    t = re.sub(rf"(пункт\w*\s+)({_NUMLIST})(\s+пункт\w*\s+)({_NUM})",
               lambda m: m.group(1) + re.sub(r"\d+", lambda d: "\x00" + d.group(0), m.group(2))
               + m.group(3) + "\x01" + m.group(4) + "\x01", t)
    t = re.sub(rf"(пункт\w*\s+)({_NUMLIST})",
               lambda m: m.group(1) + _plink(m.group(2)), t)
    t = re.sub(r"\x01(\d+)\x01", lambda m: _plink(m.group(1)), t)
    return t.replace("\x00", "")


def fmt(text):
    return link_points(inline(text))


def figure_html(fname, caption):
    svg = expand_scene_signs((ILL / fname).read_text(encoding="utf-8").strip())
    return f'<figure>{svg}<figcaption>{caption}</figcaption></figure>'


lines = MD.read_text(encoding="utf-8").splitlines()

title = "ПДД Армении"
intro = ""
chapters = []
body = []
in_toc = False
current_point = None  # номер пункта, блок которого сейчас идёт
block_text = []       # md-текст текущего блока (для поиска упомянутых знаков)


def flush_figure():
    """Вставить иллюстрацию и полоску знаков после завершившегося блока пункта."""
    global current_point, block_text
    if current_point in FIGURES:
        body.append(figure_html(*FIGURES[current_point]))
    strip = signs_strip(" ".join(block_text))
    if strip:
        body.append(strip)
    current_point = None
    block_text = []


for raw in lines:
    line = raw.strip()
    if not line:
        continue
    if line.startswith("# "):
        title = line[2:].strip()
        continue
    if line.startswith("> "):
        intro = inline(line[2:])
        continue
    if line.startswith("## "):
        h = line[3:].strip()
        if h.lower() == "оглавление":
            in_toc = True
            continue
        in_toc = False
        flush_figure()
        cid = slug_chapter(h)
        chapters.append((cid, h))
        body.append(f'<h2 id="{cid}">{inline(h)}</h2>')
        continue
    if in_toc:
        continue
    m = re.match(r"\*\*(\d+)\.?\*\*\.?\s*(.*)", line)
    if m:
        flush_figure()
        n = int(m.group(1))
        current_point = n
        block_text.append(m.group(2))
        body.append(f'<p id="p{n}"><span class="num">{n}.</span> {fmt(m.group(2))}</p>')
        continue
    block_text.append(line)
    if re.match(r"\d+\)|[абвгд]\.\s", line):
        body.append(f'<p class="sub">{fmt(line)}</p>')
        continue
    body.append(f"<p>{fmt(line)}</p>")

flush_figure()

nav = "".join(f'<a href="#{cid}">{inline(short_title(t))}</a>' for cid, t in chapters)

html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚦</text></svg>">
<style>{CSS}</style>
</head>
<body>
<button class="burger" onclick="document.body.classList.toggle('navopen')" aria-label="Оглавление">☰ Оглавление</button>
<div class="layout">
<aside>
<div class="brand">ПДД Армении</div>
{nav}
</aside>
<main>
<h1>{title}</h1>
<p class="intro">{intro} Схемы — к ключевым пунктам всех глав; знаки на схемах подписаны.</p>
{chr(10).join(body)}
</main>
</div>
<script>
var navLinks = Array.prototype.slice.call(document.querySelectorAll('aside a'));
navLinks.forEach(function(a) {{
  a.addEventListener('click', function() {{ document.body.classList.remove('navopen'); }});
}});
var headings = navLinks.map(function(a) {{
  return document.getElementById(a.getAttribute('href').slice(1));
}}).filter(Boolean);
var activeLink = null;
function updateActive() {{
  var y = window.scrollY + 90;
  var current = headings[0];
  for (var i = 0; i < headings.length; i++) {{
    if (headings[i].offsetTop <= y) current = headings[i]; else break;
  }}
  var link = current && document.querySelector('aside a[href="#' + current.id + '"]');
  if (link === activeLink) return;
  if (activeLink) activeLink.classList.remove('active');
  activeLink = link;
  if (activeLink) {{
    activeLink.classList.add('active');
    activeLink.scrollIntoView({{block: 'nearest'}});
  }}
}}
var spyTick = false;
window.addEventListener('scroll', function() {{
  if (spyTick) return;
  spyTick = true;
  requestAnimationFrame(function() {{ spyTick = false; updateActive(); }});
}}, {{passive: true}});
updateActive();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(f"OK: {OUT} ({OUT.stat().st_size // 1024} KB), глав: {len(chapters)}, иллюстраций: {len(FIGURES)}")
