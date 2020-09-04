# MocaUsersApi
[Sanic](https://github.com/huge-success/sanic) フレームワークをベースとして開発された、ユーザー関係の機能を提供するAPIサーバー。
HTTP通信を用いて任意のプログラム言語から利用可能。

### システム要件
- Python >= 3.7
- Linux or macOS (Windows未対応)
- 依存ライブラリ一覧
```
pytz
GitPython
aiosmtplib
PyMySQL==0.9.2
aiomysql
aiofiles
aioredis
requests
pymysql-pooling
sanic
ujson
aiohttp
cchardet
aiodns
docopt
pycryptodome
leveldb
twilio
limits
redis
mycli
litecli
setproctitle
tinydb
Pillow
```

### 起動方法
#### 注意: 起動前にconfig.jsonファイル内の設定をご自身の環境に合わせて変更する必要があります。
```bash
git clone https://github.com/el-ideal-ideas/MocaUsersAPI.git
cd ./MocaUsersAPI
python3 -m pip install -r requirements.txt
python3 moca.py run
```

### API使用方法
HTTP通信の`GET、 POST、OPTIONS`メソッドを利用可能。
リクエストパラメータの送信方法は、`URLパラメータ`、`JSON形式の辞書データ`、`HTMLのformタグ`、`HTTP通信のヘッダー情報`を使用可能。
但しHTMLのヘッダー情報を使用する場合のみ、リクエストパラメータをすべて大文字に、`_`を`-`に変換する必要がある。

### APIキー権限
```
-RO-: 最上位権限、すべての機能にアクセス可能
-SM-: システム管理権限、重大な影響を及ぼす機能にアクセス可能。
-NR-: 一般権限、フロントアプリケーション用の権限、万が一流出しても他のユーザーの個人情報などにアクセスできない。
```

### システムアカウント権限
-RO-: 最上位権限、すべての機能にアクセス可能
-MU-: ユーザー管理権限、他のユーザーのアカウントの制御機能を利用可能

### システムアカウント
システムアカウントは通常のアカウントと異なり、アクセストークンとパスワードは同じであり、アクセストークンの有効期限はない。
また、与えた権限により、通常アカウントでは許可されない一部の機能を使用できる。
システムの調整、デバッグなどに使用することが可能。
またアクセストークンが固定であるため、アプリケーションなどに埋め込んで特定の機能の実装に用いることもできる。
なおシステムアカウントはログイン機能によるアクセストークンの取得は不可能。

### デフォルトアカウント一覧
- Administrator(システムアカウント)
    ID: moca.administrator
    Pass: moca-moca-moca
    Permission: -RO-
- UserAdmin(システムアカウント)
    ID: moca.user-admin
    Pass: moca-moca-moca
    Permission: -MU-
- PublicUser(システムアカウント)
    ID: moca.public
    Pass: moca-moca-moca
    Permission: なし
- SupportUser(システムアカウント)
    ID: moca.support
    Pass: moca-moca-moca
    Permission: なし
- DebugAccountA(システムアカウント)
    ID: DebugAccountA
    Pass: moca-moca-moca
    Permission: なし
- DebugAccountB(システムアカウント)
    ID: moca.debug-b
    Pass: moca-moca-moca
    Permission: なし
- DebugAccountC(通常アカウント)
    ID: moca.debug-c
    Pass: moca-moca-moca
- DebugAccountD(通常アカウント)
    ID: moca.debug-d
    Pass: moca-moca-moca
    
#### ユーザーストレージ(key-value型ストレージ)について
フロントアプリケーションで機能拡張を行うために任意のデータを保存するためのストレージが0から7の8つあります。
ストレージ0と1は公開ストレージであり、他のユーザーでも取得可能。
2から7は非公開ストレージであり、保存したユーザー自身しかアクセスできない (-MU-権限以上をもつシステムアカウント除く)。
ストレージ0から5は最大保存サイズ65,535バイト。
ストレージ7から8は最大保存サイズ16Mバイト。
ユーザーストレージの操作はAPIを使用して操作可能。

#### 拡張ストレージ(mysqlベースストレージ)について
任意のデータを保存可能なストレージ、1つのキーに対して複数のデータを保存可能。
mysqlをベースにしており、insert, select, delete updateなどの機能を使用可能。
１つあたりのデータサイズ上限は16Mバイト
すべてのデータはデータを保存したユーザーアカウントからのみアクセス可能である。
ユーザーストレージ同様、API経由で操作可能。

### 共通レスポンス
- 時間あたりのリクエスト数が制限を超えた場合
    - レスポンス(403): `too many requests.`
- API-KEY認証エラー
    - レスポンス(403): `unknown api key.`
    - レスポンス(403): `api_key format error.`
    - レスポンス(403): `invalid referer.`
    - レスポンス(403): `too many requests.`
    - レスポンス(403): `you reached the access limit.`
    - レスポンス(403): `permission error.`

### API一覧
#### システムバージョンの取得
- URL: `/users/version`
- リクエストパラメータ: なし
- API-KEY: 必要なし
- レスポンス(200): バージョン番号を示す文字列

#### ダミーデータの挿入
- URL: `/users/insert_dummy_data`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - root_pass: APIサーバーの管理パスワード (半角英数字、記号などのアスキーコードで処理可能な文字列、8文字以上32文字以内)
- API-KEY: システム管理権限
- レスポンス(200): `success.`
- レスポンス(403): `root password format error.`
- レスポンス(403): `invalid root password.`

#### 新規ユーザー作成
- URL: `users/create_user`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - username: ユーザーの表示名 (デフォルト設定の場合、32文字以内のUTF-8で処理可能な任意な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - email: ユーザーのメールアドレス (デフォルト設定の場合、省略可能)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: create user successfully.
1: can't use this user id.
40: user name must be a string.
41: user name length error.
42: only ASCII characters allowed in username.
50: password must be a string.
51: password length error.
52: password must contains a alphabet.
53: password must contains a number.
54: password must contains a symbol.
55: password must only contains ascii characters.
56: password must contains upper case characters.
57: password must contain lower case characters.
60: userid must be a string.
61: user id length error.
62: user id already exists.
63: user is must only contains ascii characters.
70: email must be a string.
71: email is too long.
72: email is required.
73: email format error.
```

#### ユーザーIDチェック
- URL: `/users/check_userid`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: unknown user.
1: user id already exists.
60: user id must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### メールアドレス確認メール送信
- URL: `/users/send_email_verify_message`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: send verification code successfully.
1: unknown user.
2: already verified.
3: too quickly.
4: can't send verification code.
5: this account do not have a email address.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### メールアドレス登録(確認メール送信)
- URL: `/users/add_email_address`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - email: ユーザーのメールアドレス (デフォルト設定の場合、省略可能)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
70: email must be a string.
71: email is too long.
73: email format error.
```

#### メールアドレス認証
- URL: `/users/verify_email`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - token: 登録済みメールアドレスに送信されたトークン (6文字の半角英数字)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: verification successfully.
1: unknown user.
2: already verified.
3: token error.
4, token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### アクセストークン状態チェック
- URL: `/users/check_access_token`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: 登録済みメールアドレスに送信されたトークン (6文字の半角英数字)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: correct.
1: incorrect token.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ログイン
- URL: `/users/login`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-2: ip format error.
-1: verification code send to your phone.
0: <access token>.
1: unknown user.
2: this user account was locked by system.
3: this user account was locked by user.
4: system account can not login.
5: unknown user status.
6: please verify your email address. before login.
7: incorrect password.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
50: password must be a string.
51: password length error.
52: password must contains a alphabet.
53: password must contains a number.
54: password must contains a symbol.
55: password must only contains ascii characters.
56: password must contains upper case characters.
57: password must contain lower case characters.
```

#### ログイン用認証コードをSMSで登録済み電話番号に送信
- URL: `/users/send_phone_login_code`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - phone: 登録済み電話番号の下4桁 (半角数字4桁)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-1: phone format error.
0: verification code send to your phone.
1: unknown user.
2: this user account was locked by system.
3: this user account was locked by user.
4: system account can not login.
5: unknown user status.
6: too quickly.
7: please verify your email address. before login.
8: please verify your phone number. before login.
9: incorrect phone number.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### SMS認証コードによるログイン
-URL: `/users/login_by_phone`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - token: SMS送信された認証トークン (6文字半角英数字)
    - phone: 登録済み電話番号の下4桁 (半角数字4桁)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-3: ip format error.
-2: phone format error.
-1: invalid verification code.
1: unknown user.
2: this user account was locked by system.
3: this user account was locked by user.
4: system account can not login.
5: unknown user status.
6: please verify your email address. before login.
7: please setup your phone number, before login.
8: token format error.
9: incorrect phone number.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザー名による検索
- URL: `/users/search_users_by_name`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - username: 検索したい名前 (512文字以内のUTF-8で処理可能な任意な文字列、スペースで区切ることでand検索可能)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <a list of user's info> (id, name, profile, storage0, storage1, created_at)
1: name must be a string.
2: name is too long.
```

#### ユーザーIDによる検索
-URL: `/users/search_user_by_id`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <user info> (id, name, profile, storage0, storage1, created_at)
1: unknown user id.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 複数ユーザー検索(ユーザー名&ID)
-URL: `/users/search_users`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - keywords: 検索内容 (512文字以内の文字列からなる最大長64のリスト)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ(それぞれのキーワードに対して、ID検索及びユーザー名検索を行い、該当する内容があるものを纏めたリスト、リスト内のデータ形式はID検索やユーザー名検索の場合と同じ)

#### ユーザープロファイルの変更
- URL: `/users/save_profile`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - profile: ユーザーのプロファイルデータ (2048文字以内のUTF-8で処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: save profile successfully.
1: incorrect token.
2: profile too long.
3: token format error.
4: profile must be a string.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザープロファイル取得
- URL: `/users/get_profile`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <profile>
1: unknown user.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザープロファイル取得(複数同時)
- URL: `/users/get_profiles`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid_list: ユーザーIDのリスト (最大長64)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ (検索結果を纏めたリスト、リスト内のデータ形式は単独取得の場合と同じ)

#### 電話番号登録
- URL: `/users/add_phone_number`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - phone: 登録済み電話番号の下4桁 (国コードから始まる電話番号)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: phone number format error.
3: token format error.
4: too quickly.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 電話番号認証
- URL: `/users/verify_phone`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - code: SMSで送信された認証コード (6文字の半角英数字)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: incorrect verification code.
3: token format error.
4: already verified.
5: too quickly.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 認証済み電話番号があるかどうかをチェック
- URL: `/users/has_verified_phone`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): 認証済み電話番号がある場合は0ない場合は1を返す。

#### パスワードが正しいかどうかをチェック
- URL: `/users/check_password`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): 正しい場合は0正しくない場合は1を返す。

#### 二段階認証をオンにする
- URL: `/users/start_two_step_verification`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect password.
2: please setup your phone number.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 二段階認証をオフにする
- URL: `/users/stop_two_step_verification`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect password.
2: please setup your phone number.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### システムアカウントの権限チェック
- URL: `/users/check_system_account_permission`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - permission: 権限 (32文字以内のUTF-8で処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): 権限がある場合は0ない場合は1を返す。

#### ログインログを取得
- URL: `/users/get_my_login_log`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <login log> (id, ip, info, status, date)
1: incorrect token.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 指定ユーザーのアクセストークンを取得
- URL: `/users/get_user_access_token`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - target_userid: アクセストークンを取得したいアカウントのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: access token
1: permission denied.
2: target userid format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 自分のアカウントを停止する
- URL: `/users/lock_my_account`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect password.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 指定ユーザーのアカウントを凍結する
- URL: `/users/lock_user_account`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - target_userid: アクセストークンを取得したいアカウントのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect password or permission.
2: target userid format error.
60: user id must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### データベース初期化
- URL: `/users/reset_user_database`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - root_pass: APIサーバーの管理パスワード (半角英数字、記号などのアスキーコードで処理可能な文字列、8文字以上32文字以内)
- API-KEY: システム管理権限
- レスポンス(200): `success.`
- レスポンス(403): `root password format error.`
- レスポンス(403): `invalid root password.`

#### ユーザー関連画像の保存 (画像保存時にjpeg形式に変換され、メタデータも削除される)
- URL: `/users/save_user_image`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: 画像識別キー (64文字以内のUTF-8で処理可能な文字列)
    - image: 画像データ (バイナリデータか、base64エンコードされたデータ。保存上限10MB)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: image format error.
3: token format error.
4: image size is too large.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザー関連の画像取得
- URL: `/users/get_user_image`
- リクエストパラメータ
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - key: 画像識別キー (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: なし
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <image data> (base64形式)
2: unknown data.
4: key is too long.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザー関連の画像取得 (バイナリデータ取得)
- URL: `/users/get_user_image/<userid>/<key>`
- リクエストパラメータ
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - key: 画像識別キー (64文字以内のUTF-8で処理可能な文字列)
- レスポンス(200): 画像のバイナリデータ
- レスポンス(404): 該当する画像が見つからない

#### ユーザーアイコンのアップロード (画像保存時にjpeg形式に変換され、メタデータも削除される)
- URL: `/users/save_big_icon`
- URL: `/users/save_small_icon`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - icon: 画像データ (バイナリデータか、base64エンコードされたデータ。保存上限10MB)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```
###### その他
API `/users/save_user_image` のショートカットである。
keyとして`moca-user-icon-big` あるいは `moca-user-icon-small` を使用して、直接保存しても同じ。
     
#### ユーザーアイコンの取得
- URL: `/users/get_big_icon`
- URL: `/users/get_small_icon`
- リクエストパラメータ
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: なし
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <image data> (base64形式)
2: unknown data.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザーアイコン取得 (バイナリデータ)
- URL: `/users/get_big_icon/<userid>/<key>`
- URL: `/users/get_small_icon/<userid>/<key>`
- リクエストパラメータ
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - key: 画像識別キー (64文字以内のUTF-8で処理可能な文字列)
- レスポンス(200): 画像のバイナリデータ
- レスポンス(404): 該当する画像が見つからない

#### ユーザー関連のファイルを保存
- URL: `/users/save_user_file`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
    - data: データ (バイナリデータか、base64エンコードされたデータ。保存上限256MB)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
3: token format error.
4: key format error.
5: key is too long.
6: data is too large.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザー関連のファイルを取得
- URL: `/users/get_user_file`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <data> (base64形式)
1: incorrect token.
2: unknown data.
3: token format error.
4: key format error.
5: key is too long.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザー関連のファイルを取得 (バイナリデータ)
- URL: `/users/get_user_file/raw`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): ファイルのバイナリデータ
- レスポンス(404): 該当するファイルが見つからない

#### 他のユーザーにシステム内メールを送信
- URL: `/users/send_message`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - from: 自分のユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - to: 相手のユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - message: メッセージ内容 (8192文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: unknown target userid.
3: token format error.
4: message is too long.
5: message format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 自分宛てのシステム内メールを取得
- URL: `/users/get_messages`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - start: 取得開始メッセージ番号 (0以上の整数値)
    - limit: 取得数上限 (0以上の整数値)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <message list> (id, from_, message, time)
1: incorrect token.
2: invalid start or limit parameter.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### パスワード変更
- URL: `/users/change_password`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - old: 古いパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - new: 新しいパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: failed.
2: new password format error.
```

#### 有効なメールアドレスが登録済みかどうかを取得
- URL: `/users/has_verified_email`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: 一般権限
- レスポンス例(200) 有効なメールアドレスが登録済みの場合は0、登録済みではない場合は1を返す

#### 指定ユーザーのメールアドレス取得
- URL: `/users/get_user_email_list`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid_list: ユーザーIDのリスト (最大長1024)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ(IDとメールアドレスの辞書データ)

#### 指定ユーザーのメールアドレスにメールを送信
- URL: `/users/send_email_to_users`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid_list: ユーザーIDのリスト (最大長1024)
    - title: メールのタイトル (64文字以内のUTF-8で処理可能な文字列)
    - body: メール本文 (16384文字以内のUTF-8で処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ (送信に成功したユーザーのユーザーIDリスト)

#### 指定ユーザーの電話番号を取得
- URL: `/users/get_user_phone_number`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid_list: ユーザーIDのリスト (最大長1024)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ(IDと電話番号の辞書データ)

#### 指定ユーザーSMSを送信
- URL: `/users/send_sms_to_users`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid_list: ユーザーIDのリスト (最大長1024)
    - body: メール本文 (1024文字以内のUTF-8で処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ (送信に成功したユーザーのユーザーIDリスト)

#### 登録済みのメールアドレスまたは電話番号にパスワードリセット用トークンを送信
- URL: `/users/forgot_password`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-1: need a valid email or phone number.
0: send email successfully.
1: send sms successfully.
2: send email failed.
3: send sms failed.
```

#### トークンを使用して、パスワードをリセットする。
- URL: `/users/reset_password`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: 新しいパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - token: リセット用トークン (6文字の半角英数字)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: invalid verification code.
50: password must be a string.
51: password length error.
52: password must contains a alphabet.
53: password must contains a number.
54: password must contains a symbol.
55: password must only contains ascii characters.
56: password must contains upper case characters.
57: password must contain lower case characters.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ユーザーストレージにデータを保存
- URL: `/users/save_my_user_data`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - storage: ストレージID (0から7の整数値)
    - data: 保存するデータ (任意のデータ形式)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-1: data is too long.
0: success.
1: incorrect token.
2: invalid storage id.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 自分のユーザーストレージからデータを取得
- URL: `/users/get_my_user_data`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - storage: ストレージID (0から7の整数値)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <data>.
1: incorrect token.
2: invalid storage id.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 他のユーザーのユーザーストレージからデータを取得
- URL: `/users/get_other_user_data`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: 自分のユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - target_userid: 相手のユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - storage: ストレージID (0から7の整数値)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <data>.
1: incorrect token.
2: invalid storage id.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 他のユーザーのユーザーストレージにデータを保存
- URL: `/users/save_other_user_data`
- リクエストパラメータ
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - target_userid: 相手のユーザーID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - storage: ストレージID (0から7の整数値)
    - data: 保存するデータ (任意のデータ)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
-2: permission denied.
-1: data is too long.
0: success.
1: incorrect token.
2: invalid storage id.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 一般ユーザーの合計数を取得
- URL: `/users/get_user_count`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
- API-KEY: システム管理権限
- レスポンス(200): ユーザー数

#### ロック状態のユーザーアカウント数を取得
- URL: `/users/get_locked_user_number`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
- API-KEY: システム管理権限
- レスポンス(200): ユーザー数

#### ユーザー一覧取得 (-MU-権限をもつユーザーアカウントが必要)
- URL: `/users/get_users_list`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - password: ユーザーのログインパスワード (デフォルト設定の場合、8文字以上32文字以内のアスキーコードで処理可能な文字列)
    - start: 取得開始のインデックス (0以上の整数値)
    - limit: 取得数上限 (0以上の整数値)
- API-KEY: システム管理権限
- レスポンス(200): JSONデータ、ユーザー情報のリスト (id, status, name, email, email_verified, phone, created_at)
 
#### 拡張ストレージにデータを挿入
- URL: `/users/insert_data_to_storage`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
    - data: データ本体(任意のデータ形式)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: your data is too large.
3: token format error.
4: key format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 拡張ストレージからデータをセレクトする
- URL: `/users/select_data_from_storage`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <data> (content_id, storage, created_at)
1: incorrect token.
3: token format error.
4: key format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 拡張ストレージからデータを削除する (コンテンツID)
- URL: `/users/delete_data_from_storage_by_id`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - content_id: コンテンツID (0以上の整数値)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: content_id format error.
3: token format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 拡張ストレージからデータを削除する (データ識別キー)
- URL: `/users/delete_data_from_storage_by_key`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - key: データ識別キー (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
3: token format error.
4: key is too long.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 拡張ストレージのデータを更新 (コンテンツID)
- URL: `/users/update_data_in_storage_by_id`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - content_id: コンテンツID (0以上の整数値)
    - data: データ本体(任意のデータ形式)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: success.
1: incorrect token.
2: your data is too large.
3: token format error.
4: content_id format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### ファイル共有
- URL: `/users/share_file`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - userid: ユーザーのID (デフォルト設定の場合、32文字以内のアスキーコードで処理可能な文字列)
    - access_token: アクセストークン (システム側が発行した、32文字の認証トークン)
    - filename: ファイル名 (256文字以内のUTF-8で処理可能な文字列)
    - data: ファイル本体(base64形式またはバイナリデータ)
    - protection: パスワード (64文字以内のUTF-8で処理可能な文字列)
    - time_limit: 有効期限 (0以上の整数値、単位は秒、値が0の場合は無期限である)
    - info: 追加情報 (4096文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <access key>
1: incorrect token.
2: your data is too large.
3: token format error.
4: protection format error.
5: filename is too long.
6: time limit format error.
7: info format error.
60: userid must be a string.
61: user id length error.
63: user is must only contains ascii characters.
```

#### 共有ファイル取得 (base64)
- URL: `/users/get_shared_file`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - key: 共有されたアクセスキー (32文字の半角英数字)
    - protection: パスワード (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): JSONデータ
```json
{
  "status_code": "ステータスコード",
  "msg": "レスポンス詳細"  
}
```
- レスポンス例(200)
```
ステータスコード: レスポンス詳細
0: <data, filename, info>
1: time out.
2: file not found.
3: key format error.
4: protection format error.
5: incorrect password.
```

#### 共有ファイル取得 (バイナリデータ)
- URL: `/users/get_shared_file/raw`
- リクエストパラメータ:
    - api_key: APIサーバーのアクセスキー (システム側が発行した、長さ256の文字列)
    - key: 共有されたアクセスキー (32文字の半角英数字)
    - protection: パスワード (64文字以内のUTF-8で処理可能な文字列)
- API-KEY: 一般権限
- レスポンス(200): バイナリデータ
- レスポンス(404): ファイルを取得できません。
