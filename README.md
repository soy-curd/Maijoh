# Maijoh

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
