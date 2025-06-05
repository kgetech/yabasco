param(
    [Parameter(Mandatory=$False, Position=0, ValueFromPipeline=$false)]
    [System.String]
    $update,

    [Parameter(Mandatory=$False, Position=1, ValueFromPipeline=$false)]
    [System.String]
    $lab,
	
	[Parameter(Mandatory=$False, Position=2, ValueFromPipeline=$false)]
    [System.String]
    $yabasco
)

Write-Host $update
Write-Host $lab
Write-Host $yabasco

#Start virtual environment
. .\.venv\Scripts\Activate.ps1

# From inside your project folder (where “venv” lives):
$env:PROJECT_ROOT = (Get-Location).Path

# Point Jupyter’s config folder to .\.jupyter\config
$env:JUPYTER_CONFIG_DIR = "$env:PROJECT_ROOT\.jupyter\config"

# Point Jupyter’s data files (extensions, kernelspecs, etc.) to .\.jupyter\data
$env:JUPYTER_DATA_DIR = "$env:PROJECT_ROOT\.jupyter\data"

# Point Jupyter’s runtime (kernel summaries, security tokens, socket files) to .\.jupyter\runtime 
$env:JUPYTER_RUNTIME_DIR = "$env:PROJECT_ROOT\.jupyter\runtime"

#Update 
if($update -eq "Y"){
	pip install -r requirements.txt
}

if($lab -eq "Y") {
	jupyter notebook --generate-config
	jupyter lab --generate-config
	jupyter lab
}

if($yabasco -eq "Y") {
	#Start main script
	python .\src\yabasco.py
}

