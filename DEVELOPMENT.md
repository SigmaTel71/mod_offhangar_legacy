# Prerequisites
## PjOrion
Grab [Python 2.6.6 x32](https://www.python.org/downloads/release/python-266/) and pack its native runtime library and standard library to PjOrion. Alternatively, extract two files from [this archive](https://k2mg.net/res/storage/python26.7z) into your PjOrion folder and change your Python library to `python26.dll` via **Terminal** -> **Settings** -> **Basic setup**.

<details><summary>Example settings</summary>

![image](https://github.com/SigmaTel71/mod_offhangar_legacy/assets/17989678/a012b37e-4d07-4d4b-b2fd-81aac811cde5)

</details>

## IDE setup
> [!IMPORTANT]
> Setup pipeline for other IDEs and "code editors" may and will vary. Non-Windows environments are not covered by this guide as these are not supported.

### Sublime Text 4
Before creating a development project, do the following:
1. Install these packages via Package Control:
    - [LSP](https://packagecontrol.io/packages/LSP), [LSP-pylsp](https://packagecontrol.io/packages/LSP-pylsp), [LSP-json](https://packagecontrol.io/packages/LSP-json) (optional)
    - [Run Apps](https://packagecontrol.io/packages/Run%20Apps)
2. Add PjOrion as a [build system](https://www.sublimetext.com/docs/build_systems.html):
```json
{
    "shell_cmd": "\"D:\\Program Files (x86)\\PjOrion\\PjOrion.exe\" /compile-folder \"$project_path\" /exit"
}
```
3. Target World of Tanks client added as an application for Run Apps (**Tools** -> **Run Apps** -> **Add Application**):
> [!WARNING]
> **This package does not support project-specific settings.**
> Once added, this executable will be globally available to all projects via Command Pallette (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>).
```json
[
  {
      "caption": "Run: World of Tanks 0.8.2 #349 (RU)",
      "command": "runapp",

      "args": {
          "app": "D:\\Games\\World of Tanks 0.8.2 (RU)\\WorldOfTanks.exe"
      }
  }
]
```
4. Backup your `paths.xml` file in targeted World of Tanks client and then edit it to include `mod_offhangar_legacy` folder prior to `./res_mods/0.8.2`:
```xml
<root>
  <Paths>
    <Path>G:\Git\mod_offhangar_legacy</Path>
    <Path>./res_mods/0.8.2</Path>
    <Path>./res/packages/shared_content.pkg</Path>
    <!-- ... -->
  </Paths>
</root>
```
5. Open the `offhangar.sublime-project` via **Project** -> **Open Project**. As soon as you open it, adjust paths to **decompiled** common and client-specific public World of Tanks Python scripts.
6. Build the project via **Tools** -> **Build** and then start the game by running the command you configured in setp 3.

# Contribution policies
Before you submit a pull request, ensure the following:
- your code submissions do not contain anything made with AI;
  - exception applies only if there is only one possible implementation
    - this does not dismiss the requirement from the submitter to manually review the submitted code and explain what it does in the pull request
- you were not tainted by possession of proprietary code owned by Wargaming Group Limited, this includes:
  - possession or witnessing server-side code not bundled with the World of Tanks client;
  - use of leaked BigWorld Technology middleware, including the "2014 OSE" release of unknown copyright status.