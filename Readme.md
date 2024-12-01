# easy-whisper
## How to use
0. 環境変数を設定
export API_KEY = "sk_hogehoge"

1. Dockerイメージをビルド
docker build -t easy-whisper .

2. コンテナを起動
docker run -p 5000:5000 easy-whisper
