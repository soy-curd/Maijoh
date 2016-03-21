# Maijoh

## Download Kakuyomu text

```python
import download
kakuyomu = download.Kakuyomu()
novels = kakuyomu.get_novel_link("ほげ")
```

## setup(for Mac OS)

### tensorflow
```
pip install --upgrade https://storage.googleapis.com/tensorflow/mac/tensorflow-0.6.0-py3-none-any.whl
```

### mongoDB

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
