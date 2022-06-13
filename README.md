# A-RE Android
Android applications reverse-engineering utility <br> (pretty simple at the moment, but who knows whats coming up next..) <br><br><br>
![image](https://user-images.githubusercontent.com/37783231/172968610-66a7b7bb-c127-4e5f-9d6a-7ea3d051cb53.png)
![image](https://user-images.githubusercontent.com/37783231/173279259-92ad82a2-38db-4fe6-8fe5-25d351a1aa5f.png)



## Current features:
- APK decompiling (de-odexing, unpacking resources etc), powered by [ApkTool](https://github.com/iBotPeaches/Apktool)
- APK re-compiling and signing (currently only test signing is supported)
- Basic APK information (like icon, package name, package version etc), powered by [PyAxmlParser](https://github.com/appknox/pyaxmlparser)
- User-friendly UI powered by Tkinter!
- Plugins support, some already shipped with application: 
    - Cocos2D plugin: capable of packing and unpacking jsc/jsc2/luac files used by Cocos2D engine

## Notes:
This project was made by me, and my python knowledge kinda sucks <br>
Don't expect to see quality code here (PR's are welcomed!) <br>
I'm working on this project at spare time, which means that no regular support of this tool will be provided
