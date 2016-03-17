# Maijoh

## Download Kakuyomu text

```python
# ほげタグの小説を検索
import download
kakuyomu = download.Kakuyomu()
novels = kakuyomu.get_novel_link("ほげ")
```

## setup(for Mac OS)

```
brew install mongodb
```

ログイン時に起動しておきたい場合は、

```
ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
```

都度起動したい場合は、
```
mongod --config /usr/local/etc/mongod.conf
```
