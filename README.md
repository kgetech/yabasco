This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

# <sup>yabasco:</sup> <sub>Yet Another BAsic Smith Chart gizmO</sub>

Copyright (C) 2025  Kyle Thomas Goodman

email: <mailto:kylegoodman@kgindustrial.com>

GitHub: <https://github.com/kgetech/>

*Made for people who had weird labs and simple needs.* 

## Installation Instructions (Vindoge 11):
Install python3 through the ms store thingy.
run setup_env.ps1 from a user-level (not administrative) powershell console.

*If you can't execute the .ps1 script:*
From an administrative powershell console run:
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

## For BASH/\*nix: Coming soon. 
*Basically just do the same thing, but in penguin or wildebeest or whatever.*   
*ALSO: chmod +x can come in digdogdangdandily.*
Release Info:


## Project Journal

### 2025-06-07 07:18 PM: Rewriting Begins
- Gutted the project
- Added a main_window module
- Added a data_management module
  - Window Settings
  - Chart Settings
  - Chart Objects (impedances, etc)
    - Chart Object Settings (line colors, styles, labels, etc)
  - Session Save and Load Serialization (WIP)
    - Seems saving to .yaml works reasonably well

### 2025-06-07 01:17 PM: v0.0.2
- Final working version built with ChatGPT: Rebuilding the project from scratch after this commit. 
- This release is to look at how far the project could get with ChatGPT alone, and for reviewing some of the code implementations. 

### 2025-05-21 03:23 PM: 
- ~~Fix the labels on the chart curves~~
- Add more labels (all of them)
- Make points draggable
- Allow multiple impedance entries
- Report the cursor position below the cursor
- More Testing
- Other Features? 