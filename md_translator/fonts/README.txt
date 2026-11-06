Noto Serif TC (Traditional Chinese), SIL Open Font License 1.1.
Source: https://github.com/google/fonts/tree/main/ofl/notoseriftc
Upstream font: NotoSerifTC[wght].ttf
License: OFL-NotoSerifTC.txt

The bundled WOFF2 files are static instances at wght=400 and wght=700,
created with fonttools 4.68.0 and brotli 1.2.1:

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
for weight, name in [(400, 'Regular'), (700, 'Bold')]:
    font = TTFont('NotoSerifTC[wght].ttf')
    instantiateVariableFont(font, {'wght': weight}, inplace=True, updateFontNames=True)
    font.flavor = 'woff2'
    font.save(f'NotoSerifTC-{name}.woff2')

No runtime font download or fonttools installation is needed.
