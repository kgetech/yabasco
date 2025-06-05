###########################################################################################
## yabasco: Yet Another BAsic Smith Chart gizmO
## Copyright (C) 2025  Kyle Thomas Goodman
## email: kylegoodman@kgindustrial.com
## GitHub: https://github.com/kgetech/
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################################

param(
    [Parameter(Mandatory=$False, Position=0, ValueFromPipeline=$false)]
    [System.String]
    $jupyter

)

Write-Host $jupyter


# Activate the venv
. .\.venv\Scripts\Activate.ps1


if($jupyter -eq "Y"){
	# From inside your project folder (where “venv” lives):
	$env:PROJECT_ROOT = (Get-Location).Path

	# Point Jupyter’s config folder to .\.jupyter\config
	$env:JUPYTER_CONFIG_DIR = "$env:PROJECT_ROOT\.jupyter\config"

	# Point Jupyter’s data files (extensions, kernelspecs, etc.) to .\.jupyter\data
	$env:JUPYTER_DATA_DIR = "$env:PROJECT_ROOT\.jupyter\data"

	# Point Jupyter’s runtime (kernel summaries, security tokens, socket files) to .\.jupyter\runtime 
	$env:JUPYTER_RUNTIME_DIR = "$env:PROJECT_ROOT\.jupyter\runtime"
	
	# Jupyter Generate Config
	jupyter notebook --generate-config
	jupyter lab --generate-config

	# Start jupyter
	jupyter lab
} else {
	# Start The Program
	python .\src\yabasco.py
}



