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

# Create virtual environment
py -3.10 -m venv .venv

# Activate the venv
. .\.venv\Scripts\Activate.ps1

# Get Latest PIP
python.exe -m pip install --upgrade pip

# Install requirements
pip install numpy scikit-rf pyqt5 matplotlib pyyaml requests

if($jupyter -eq "Y"){
	# From inside your project folder (where “venv” lives):
	$env:PROJECT_ROOT = (Get-Location).Path

	function Initialize-LocalDirectory {
		param (
			[string[]]$NewDir
		)
		
		foreach ($ND in $NewDir){
			If(!(test-path -PathType container $env:PROJECT_ROOT\$ND))
			{
				  New-Item -ItemType Directory -Path $env:PROJECT_ROOT\ -Name $ND
			}
		}
	}

	Initialize-LocalDirectory -NewDir .jupyter\config, .jupyter\data, .jupyter\runtime

	# Point Jupyter’s config folder to .\.jupyter\config
	$env:JUPYTER_CONFIG_DIR = "$env:PROJECT_ROOT\.jupyter\config"

	# Point Jupyter’s data files (extensions, kernelspecs, etc.) to .\.jupyter\data
	$env:JUPYTER_DATA_DIR = "$env:PROJECT_ROOT\.jupyter\data"

	# Point Jupyter’s runtime (kernel summaries, security tokens, socket files) to .\.jupyter\runtime 
	$env:JUPYTER_RUNTIME_DIR = "$env:PROJECT_ROOT\.jupyter\runtime"
	
	# Install jupyter requirements
	pip install jupyterlab notebook voila
	
	# Jupyter Generate Config
	jupyter notebook --generate-config
	jupyter lab --generate-config
	


	# Create Requirements file
	pip freeze > requirements.txt
	
	# Start jupyter
	jupyter lab
} 





