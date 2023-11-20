#!/bin/bash

# botを配置するフォルダを作成して移動する
cd ~/
mkdir bot
cd bot
echo "アプリケーションフォルダを作成しました。"

# パッケージマネジメント
# インストーラーを最新化して、gitを入れておく
sudo yum -y update
sudo yum -y install git
sudo yum -y install python3-pip
echo "----------現在のpython versionは以下の通りです。----------"
python3 --version
echo "----------現在のpython versionは以下の通りです。----------"
python3 -m pip install -U pip

# 必要ライブラリのインストール（ここは自分が使うものを指定してください）
pip3 install ta
pip3 install copy
pip3 install pandas
pip3 install numpy
pip3 install matplotlib
pip3 install seaborn
pip3 install warnings
pip3 install requests
pip3 install git+https://github.com/bitbankinc/python-bitbankcc@master\#egg=python-bitbankcc
echo "基本パッケージのインストールを実行しました。"

# 日本語のロケールが存在するかを確認
if ! locale -a | grep -q "ja_JP.utf8"; then
    # 日本語のロケールを追加
    sudo locale-gen ja_JP.utf8
fi

# システムのデフォルトロケールを日本語に設定
sudo update-locale LANG=ja_JP.utf8

# 現在のシェルセッションのロケールを日本語に変更
export LANG=ja_JP.utf8
echo "ロケールを日本語に設定しました。"

# 停止用スクリプトファイルを作って、実行権限を付与しておく
echo "停止用スクリプトファイル作成開始"
touch stop.sh
chmod +x stop.sh

cat > stop.sh << "EOF"
#!/bin/bash

# プログラム名を引数から取得
PROGRAM_NAME=$1

# プログラム名が指定されていない場合はエラーメッセージを表示して終了
if [ -z "$PROGRAM_NAME" ]; then
    echo "プログラム名を指定してください。"
    exit 1
fi

# プログラム名でプロセスを検索し、プロセスIDを取得
PIDS=$(ps aux | grep "$PROGRAM_NAME" | grep -v "grep" | awk '{print $2}')

# プロセスIDが存在する場合、それぞれのプロセスを終了
if [ -z "$PIDS" ]; then
    echo "該当するプロセスは見つかりませんでした。"
else
    for PID in $PIDS; do
        kill -9 $PID
        echo "プロセスID $PID を終了しました。"
    done
fi
EOF
echo "停止用スクリプトファイル作成完了"
echo "nohupで動かしたプログラムを止めるコマンドは以下の通りです。"
echo "bash stop.sh <ファイル名>.py"