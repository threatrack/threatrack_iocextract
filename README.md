# threatrack_iocextract.py

Extracts IOCs (and other patterns) from text.

## How do I use it?

### Install

- from `https://pypi.org` via `pip`:

```
pip install threatrack_iocextract
```

- via `setup.py`:

```
sudo python setup.py install
```

### Usage

```python
import threatrack_iocextract

text = 'hxxp://bad[.]com/  https://evil.com/foobar?a=1 asfdas\nsadfasf bob at example dot com'

# extract IOCs
iocs1 = threatrack_iocextract.extract(text)
# iocs1 is dict like `{ioctype1 : [ioc1, ioc2, ...], ioctype2 : [ioc3, ...], ...}`
print(iocs1['url'][0]) # prints https://evil.com/foobar?a=1
print(iocs1['hostname'][0]) # prints evil.com

# extract defangled IOCs
iocs2 = threatrack_iocextract.extract_all(text)
print(iocs2['url'][0]) # prints http://bad.com/
print(iocs2['hostname'][0]) # prints bad.com
print(iocs2['email'][0]) # prints bob@example.com

```

## How does this work?

### `threatrack_iocextract.py`

The main python program. The workflow is:

1. `load_patterns()`: Read, expand and configure search patterns (automatically called on import).
2. `refang(text)`: Turns defanged `text` into "refanged" text, e.g. 'hxxp://bad[.]com/' becomes 'http://bad.com/'.
3. `extract(text)`: Extract IOCs from `text`. Returns a dict like `{ioctype1 : [ioc1, ioc2, ...], ioctype2 : [ioc3, ...], ...}` (see [How do I use it?])
4. `extract_all(text)`: Like `extract()` but will also extract defanged IOCs.

### `patterns/`

Contains the search pattern configuration.

#### `patterns/patterns.csv`

A tab separated list of search patterns.
This is loaded by `load_patterns()`.
The format is **tab separated**:

```
ioctype	regexpattern	regexoptions
```

It **must always have 3 columns**.

For example:

```
sha1	\b[a-f0-9]{40}\b	i
```

would search for SHA1 hashes between word boundaries.

Possible options are:

- `i` (= re.I = case-insensitive)
- `s` (= re.S = dot all)

All other `regexoptions` are ignored. `regexoptions` **must** be set (even if just an empty character)!

**Expansions** allow you to reuse other sources in patterns. There are two types
of expansions:

- `%%file:name.csv%%`
- `%%pattern:name%%`

**file:** expansions allow to include file contents in patterns.
`name.csv` is a file with single column list of patterns. Any pattern containing
this expansion will replace `%%file:name.csv%%` with a regex trying to match each
line of `name.csv`.

For example, if `name.csv` contains:

```
foo
bar
shoot
```

The pattern `test%%file:name.csv%%?blah' will be expanded to `test(?:foo|bar|shoot)?blah'.
See `patterns/{schemes,tlds}.csv` for how this can be useful.

**pattern:** expansions allow to reuse **previous** patterns.

For example, if `patterns.csv` contains:

```
.port	6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[0-9]	.
ipv4	(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\:%%pattern:.port%%)?	.
```

`ipv4` would be expanded to:

```
(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\:(?:6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-5][0-9]{4}|[1-9][0-9]{3}|[1-9][0-9]{2}|[1-9][0-9]|[0-9]))?
```

**Names starting with `.` (dot) are private.** They are not searched directly
but can be used in expansions.

### Gotchas

- `tlds.csv` and `schemes.csv` must be sorted longest patterns first to ensure longest match. Otherwise `.co` would match before `.com`, etc.



## Are there any issues?

Yes. Unfortunately, I can only list the known issues.

### Known issues

#### Unconditional refangle

`extract_all(text)` will refang the text. This could potentially lead to altered
IOCs, e.g. `I am at home.To do so ...` would be altered to `I am@home.To do so ...`
and thus lead to the email IOC `am@home.to`.

Other possibilities are that IOCs get altered, e.g. `http://example[.]com/foo[dot]bar/`
would refangle to `http://example.com/foo.bar/`.

Unfortunately, it is very hard to fix this. **Suggestions are welcome.**


## TODO

- Fix IPv6 pattern, it overlaps with MAC addresses
- Fix Hash and Bitcoin overlap
- Increase whitelist
- Fix MAC pattern to not match on fingerprints
- Fix extract_all() refanging breaks YARA extraction. Need to find a smart solution to extracting defanged IOCs. :(
- Actually use `whitelist.csv`


