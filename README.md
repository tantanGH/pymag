# pymag
MAG format image file encoder in Python



令和の今、X680x0環境に最新のイメージデータ、それも正方形ピクセルの高解像度画像を持ち込もうとした場合、[BMPLEX.X](https://github.com/tantanGH#bmplexx) を使えば24bitカラーのBMPを最大65536色で表示し、高解像度768x512画面のコマンドラインの背景などに利用することができます。しかしながらこれはエミュレータ[XEiJ](https://stdkmd.net/xeij/)の独自拡張機能を前提にしているため、[X68000Z](https://www.zuiki.co.jp/products/x68000z/)を含む実機や、他のエミュレータではサポートされません。

X680x0が現役だった時代に広く利用されていた軽量画像フォーマットの一つにMAG形式がありました。これはルーツがPC98系であったため、16色もしくは256色の正方形ピクセルを前提としたフォーマットになっています。パレットも対応しています。

このpymagは任意の画像ファイルをPython上でこのMAG形式にしてファイル出力するためのライブラリでありツールです。変換元の画像の読み込みは[Pillow(import名はPIL)](https://pillow.readthedocs.io/)を利用しているため、ほぼすべての現行フォーマットの画像データであれば読み込み可能です。

---

### インストール方法

    pip install git+https://github.com/tantanGH/pymag.git

---

### 使い方

pymag はパスが通っていれば直接コマンドラインツールとして利用できます。基本的には変換元となる画像ファイル名と、変換先となるMAGファイル名を与えるだけです。

    pymag <input-image-filename> <output-image-filename>

ヘルプを見るには `-h` オプションまたは `--help` を使ってください。

    pymag -h
    pymag --help

また、python の `-m` オプションと共に使うこともできます。

    python3 -m pymag <input-image-filename> <output-image-filename>

ライブラリとして以下のように利用することもできます。

    import pymag

    pymag.save(infile,outfile,...)

---

## 注意事項

手元の画像である程度確認してはいますが、詳細なテストを行なったわけではありませんので、画像の一部が欠落したり、不正なファイルを出力してしまう可能性があります。
    
---

## TERMS OF USE / 免責

ここで配布されているソフトウェアを使用したことにより何らかの不具合(システムクラッシュその他)が生じても、一切の責任は負えません。自己責任にてご利用ください。


## CONTACT / 連絡先

tantan (github:tantanGH, twitter:snakGH)
