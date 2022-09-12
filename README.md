# easy-judge

提出されたコードの簡単な採点

## 使い方

- 実行条件
  - `judge.py` と `printer.py` が同じディレクトリにある
  - `easy-judge-conf.json` が pwd にある

```
python3 path/to/judge.py
```

- path/to/judge.py: judge.py へのパス

## できること

1. ディレクトリにある複数のコードの採点
2. 複数のディレクトリについて、1. を実行

### 1.

- src_dir にあるすべてのコードを対象に、そのコードを実行したときに出力された値が解答と一致するかどうかの採点ができる
- 解答は ans_dir におく
  - `コードの解答ファイル名` = `「コードファイルの拡張子より前の名前」.ans`
- つまり、採点は下の例だと次のようにおこなわれる
  - `src_dir/p01.py` の採点: 「`src_dir/p01.py` から出力された値」と「`ans_dir/p01.ans` の内容」は等しいか
  - `src_dir/p02.py` の採点: 「`src_dir/p02.py` から出力された値」と「`ans_dir/p02.ans` の内容」は等しいか
  - `src_dir/p03.py` の採点: 「`src_dir/p03.py` から出力された値」と「`ans_dir/p03.ans` の内容」は等しいか
- src_dir と ans_dir は [設定ファイル](#設定ファイル) で指定する

```
$ tree src_dir
src_dir
├── p01.py
├── p02.py
└── p03.rb

$ tree ans_dir
ans_dir
├── p01.ans
├── p02.ans
└── p03.ans
```

### 2.

- src_dirs にある複数の src_dir* に対して、[1.](#1) の処理をおこなう
- 採点の仕方は [1.](#1) と同じ
- src_dirs と ans_dir は [設定ファイル](#設定ファイル) で指定する

```
$ tree src_dirs
src_dirs
├── src_dir_1
│   ├── p01.py
│   ├── p02.py
│   └── p03.rb
└── src_dir2
    ├── p01.py
    ├── p02.py
    └── p03.rb

$ tree ans_dir
ans_dir
├── p01.ans
├── p02.ans
└── p03.ans
```

## 設定ファイル

- `easy-judge-conf.json` で必要な値を設定する
- pwd におく

```
$ cat easy-judge-conf.json
{
  "src_dirs": "./test01/",
  "src_dir": "./test01/student00",
  "ans_dir": "./test01/.ans",
  "src_langs": {
    "py": "python3",
    "rb": "ruby"
  }
}
```

- src_dirs:
  - [2.](#2) の src_dirs に当たるディレクトリへのパスを指定する
  - pwd からの相対パス、または絶対パス
- src_dir
  - [1.](#1) や [2.](#2) の src_dir に当たるディレクトリへのパスを指定する
  - [2.](#2) の処理をおこなうとき、src_dir は指定しない
  - pwd からの相対パス、または絶対パス
    - ※ 直下のディレクトリを指定する場合、先頭に `./` をつけないとエラーになる
- ans_dir
  - [1.](#1) や [2.](#2) の ans_dir に当たるディレクトリへのパスを指定する
- src_langs
  - 採点の対象とするコードについてのオブジェクト
    - key: コードの拡張子
    - value: コードの言語名
  - [paiza.IO](https://paiza.io/ja/) の API にリクエストを投げるときに、言語名が必要になるため、「コードの言語名」も指定する（[paiza.IO が対応している言語](#paizaio-が対応している言語)）

## 1. か 2. か

- src_dir がないとき、または `""` のとき、2. の処理をおこなう
- それ以外のとき、1. の処理をおこなう

## 採点結果

- `grades_book.json` に採点結果が出力される
- 各コードについて、解答と一致した場合 `O`, 一致しなかった場合 `X` 

## paiza.IO が対応している言語

- paiza.IO が対応している言語は [ここ](https://paiza.io/help) から確認できる（API のページではないが、おそらく対応言語は API も同様）
- 以下抜粋（抜粋日: 2022/09/12）

| 言語名 | バージョン |
| :-----: | :-----: |
| Java | openjdk version "18.0.2.1" 2022-08-18 |
| PHP | PHP 8.1.9 (cli) (built: Aug 15 2022 09:39:52) (NTS) |
| Ruby | ruby 3.1.2p20 (2022-04-12 revision 4491bb740a) [x86_64-linux] |
| C++ | C17++ / clang version 10.0.0-4ubuntu1 |
| C# | Mono JIT compiler version 6.8.0.105 (Debian 6.8.0.105+dfsg-2 Wed Feb 26 23:23:50 UTC 2020) |
| JavaScript | Node.js v16.17.0 |
| Go | go version go1.19 linux/amd64 |
| Python3 | Python 3.8.10 |
| MySQL | mysql Ver 8.0.30-0ubuntu0.20.04.2 for Linux on x86_64 ((Ubuntu)) |

## API

- [paiza.IO](http://api.paiza.io/docs/swagger/#!/runners/)

## 外部ライブラリ

- requests
