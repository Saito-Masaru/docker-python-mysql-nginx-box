# python + nginx + mysql のdocker環境

## 概要

python3の実行環境と併せてmysqlおよびnginxの環境。  
pythonコンテナでデータ分析をして結果をHTMLでマークアップしたデータを作成してそれをnginxで閲覧できるようにして、データは再利用可能、クエリーで絞り込みも容易なmysqlで行うことを想定した環境。  

pythonは実行環境として考えてはいるが一応WEBインターフェースとしてflaskをインストールした。  
ただし、基本コンセプトはpythonを利用してデータ分析と結果を確認で来るための環境のみで各環境は最低限の機能のみを設置している。  
なのでバッチでの実行ができれば問題ないと考えている。  

## 確認環境

```
>wsl --version
WSL バージョン: 2.2.4.0
カーネル バージョン: 5.15.153.1-2
WSLg バージョン: 1.0.61
MSRDC バージョン: 1.2.5326
Direct3D バージョン: 1.611.1-81528511
DXCore バージョン: 10.0.26091.1-240325-1447.ge-release
Windows バージョン: 10.0.22631.4169

 $ cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.4 LTS"

 $ docker --version
Docker version 27.1.1, build 6312585

$ docker-compose --version
Docker Compose version v2.29.1-desktop.1
```

なお、wslのバージョン情報でwindows10と出力されていますがPCのOSはwindows11です。

## ファイル構成

```
 $ tree
.
|-- /app
|   `-- app.py
|-- /data
|-- /docker
|   |-- /mysql
|   |   `-- my.cnf
|   |-- /nginx
|   |   `-- default.conf
|   |-- /nxinx
|   |   `-- default.conf
|   `-- /python
|       |-- Dockerfile
|       `-- requirements.txt
|-- docker-compose.yml
|-- html
|-- log
|   |-- /mysql
|   `-- /nginx
`-- /static
    |-- /css
    |-- /img/
    `-- /js
```


## ファイルとディレクトリの説明

* ディレクトリ

/data: 分析結果や再利用するデータの保管場所。各コンテナでは `/data` にマウントされ各コンテナ同士でのデータ受け渡しやホストPCとコンテナ間のデータ受け渡しにも利用可能。ただし、インターネット上など公開する場合はセキュリティ的には好ましくないのでコメントアウトすることを推奨する。  
/html: pythonでの分析結果をHTMLでマークアップして出力してブラウザから確認することを想定。pythonとnginxでマウントする。こちらもパブリックな環境では利用しないほうが望ましい。  
/static: nginxでcss,js,imgなどの静的ファイルを格納することを想定。nginxコンテナのみでマウントする。
/app: pythonのプログラムファイルを格納する想定。pythonコンテナのみでマウントする。
/log: mysqlとnginxコンテナでログの確認のためにマウントする。それぞれふぃような場合はマウントしないか設定ファイルにて背出力制御可能。  

* ファイル

.env_example: 口述しますがmysqlコンテナビルド、docker-composeコマンド実行時に参照される.envファイルのサンプル。   
docker-compose.yml: docker-composeコマンドでコンテナの設定、ビルド字に利用。  
docker/ 以下のファイル:各コンテナのビルド時に利用。また各コンテナ内にマウントする設定ファイル。  


## 各コンテナの概要

〇 python  
python3.10  
/appフォルダにapp.pyをサンプルで置いている。  *
flaskのエンドポイント

| path | 概要        |
|------|-------------|
| /    | hello flask |
| /db  | mysqlのtestテーブルの内容を出力する。<br>testテーブルがない場合は500エラーとなる。 |

port: 5000  
PCから `http://localhost:5000` にアクセスすると上記flaskにアクセス可能。

〇mysql  
mysql 8.0.39  
システムで使っている以外の初期detabaseやuser,portなどを `.env_example` をコピーして `.env` ファイルを作ってからビルドする必要があります。(後述)  
3306ポートでPC側のmysqlクライアントで接続可能です。(docker-compose.ymlファイルで変更可能)  
手元にdumpファイルがある場合は以下の手順でインポート可能です。

1. /data以下にダンプファイルを設置(/data/db.dumpとする)
1. コンテナに入る。 `docker exec -it mysql bash`
1. インポート実施　`mysql -u[user] -p [dbname] < /data/db.dump`

ログについて  
`log/mysql/query.log` は全てのSQLを記録しているためデバッグには非常に有用ですが、不要な場合は容量を消費してしまうので停止するほうが良いかもしれません。  
呈したい場合は `docker/mysql/my.cnf` の *general_log* を0にするか、コメントアウトしてmysqlコンテナをdown→upしてください。

データの保存先について
mysqlコンテナとは別に `mysql-data` というvolumeを設定しておりコンテナをリビルドしてもデータは失われません。


〇nginx
nginx 1.20

設定済みのエンドポイントは以下の通り

| path(uri) | 参照先 |
|------|--------|
| /    | /html マウントポイント:/usr/share/nginx/html             |
| /css | /static/css マウントポイント:/usr/share/nginx/static/css |
| /js  | /static/css マウントポイント:/usr/share/nginx/static/js  |
| /img | /static/img マウントポイント:/usr/share/nginx/static/img |
| /app | pythonコンテナの5000晩poert(flask) リバースproxyにて接続 |



## 起動手順

1. `.env_example` を　`.env` にコピーします。
    * `cp .env_example .env` 
1. コピーした `.env` を編集します。
    * mysqlコンテナに作るDB情報、接続port、ユーザー、パスワードなどを設定します。
    * `vi .env`
1. 適宜docker-comppose.ymlやdocker/* の設定ファイルを編集します。
1. `docker-compose up -d` と入力してenterキーを押すとコンテナの取得ビルドを自動で行い終了後に利用可能となります。

※初回以外は `docker-compose up -d` と `docker-compose down` で問題ありません。

## 各コンテナへの入り方

python: `docker exec -it python bash`

nginx: `docker exec -it nginx bash`

mysql:  
  (shell): `docker exec -it mysql bash`  
  (mysql db): `docker exec -it mysql -u[username] -p [dbname]`

基本的に全てubuntuベースなので必要なパッケージなどはaptで追加可能。(リビルドしたら消えるので永続化する場合は適宜Dockerfileや再構築用のshell scriptなどを用意すること)  

## 参考にしたページ

mysqlについて  
https://qiita.com/ucan-lab/items/b094dbfc12ac1cbee8cb

pythonについて  
https://qiita.com/syo_engineer/items/5f31f25cb50400b94b1d

以上


___

