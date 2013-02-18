# garchdeps
[![Build Status](https://secure.travis-ci.org/badele/garchdeps.png)](http://travis-ci.org/badele/garchdeps)

=========

Tool that show graphical dependencies of the archlinux packages


## Examples

#### Show tree for package
```bash
>garchdeps.py -t python

|--python 
   |--expat 
      |--glibc 
         +--linux-api-headers 
         +--tzdata 
   |--bzip2 
      |--glibc 
   |--gdbm 
      |--glibc 
      |--sh(by bash) 
         |--readline 
            |--glibc 
            |--ncurses 
               |--glibc 
         |--glibc 
   |--openssl 
      |--perl 
         |--gdbm 
         |--db 
            |--gcc-libs(by gcc-libs-multilib) 
               |--glibc 
               |--lib32-gcc-libs 
                  +--lib32-glibc 
                  |--gcc-libs(by gcc-libs-multilib) 
            |--sh(by bash) 
         |--coreutils 
            |--glibc 
            |--pam 
               |--glibc 
               |--db 
               |--cracklib 
                  |--glibc 
                  |--zlib 
                     |--glibc 
               |--libtirpc 
                  |--libgssglue 
                     |--glibc 
               +--pambase 
            |--acl 
               |--attr 
                  |--glibc 
            |--gmp 
               |--gcc-libs(by gcc-libs-multilib) 
               |--sh(by bash) 
            |--libcap 
               |--glibc 
               |--attr 
         |--glibc 
         |--sh(by bash) 
   |--libffi 
      |--glibc 
   |--zlib 
```

#### Show sorted used package
```bash
>garchdeps.py

-----------------------------------------+---------+----------+----------+----------+-----------+------------+
Package                                  | T. Deps | M. depth | N usedby |  Size    | T. Size   |  % T. Size |
-----------------------------------------+---------+----------+----------+----------+-----------+------------+
microchip-mplabx-bin                     |      10 |        6 |        0 |   553 MB |     85 MB |            |
processing                               |      90 |       11 |        0 |   377 MB |    335 MB | ###        |
qt-doc                                   |     112 |       10 |        0 |   377 MB |    509 MB | ####       |
libreoffice-common                       |      88 |        8 |       10 |   236 MB |    462 MB | ####       |
eagle                                    |      65 |        8 |        0 |   203 MB |    240 MB | ##         |
ocaml                                    |       7 |        5 |        0 |   191 MB |     62 MB |            |
virtuoso                                 |      32 |       10 |        0 |   185 MB |    255 MB | ##         |
gutenprint                               |       3 |        2 |        0 |   170 MB |     47 MB |            |
boost                                    |      13 |        6 |        1 |   143 MB |    121 MB | #          |
mono                                     |      37 |        7 |        4 |   136 MB |    153 MB | #          |
blender                                  |     153 |       10 |        0 |   122 MB |    753 MB | #######    |
mongodb                                  |      13 |        6 |        0 |   113 MB |    121 MB | #          |
chromium                                 |     118 |        9 |        0 |   111 MB |    440 MB | ####       |
webmin                                   |      24 |        6 |        0 |   107 MB |    175 MB | #          |
libreoffice-sdk-doc                      |     106 |        9 |        0 |   104 MB |      1 GB | ########## |
emacs                                    |     138 |        9 |        0 |   102 MB |    514 MB | #####      |
google-chrome                            |     131 |        8 |        0 |   101 MB |    555 MB | #####      |
catalyst-utils                           |      89 |       10 |        2 |    94 MB |    240 MB | ##         |
android-sdk                              |     121 |       11 |        1 |    94 MB |    512 MB | ####       |
python                                   |      27 |        7 |       23 |    93 MB |    187 MB | #          |

```
