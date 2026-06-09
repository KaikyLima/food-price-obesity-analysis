@echo off
echo Configurando ambiente do projeto...

:: 1. Criar ambiente virtual com Python 3.13 especificamente
if not exist ".venv" (
    echo Criando ambiente virtual com Python 3.13...
    py -3.13 -m venv .venv
    if errorlevel 1 (
        echo ERRO: Python 3.13 nao encontrado!
        echo Verifique se esta instalado: py -3.13 --version
        pause
        exit /b 1
    )
) else (
    echo Ambiente virtual ja existe.
)

:: 2. Ativar ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

:: 3. Confirmar versao do Python
echo Versao do Python:
python --version

:: 4. Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip --quiet

:: 5. Instalar dependencias do requirements.txt
echo Instalando dependencias...
pip install -r requirements.txt --quiet

:: 6. Criar pasta data se não existir
if not exist "data" (
    echo Criando pasta data...
    mkdir data
) else (
    echo Pasta data ja existe.
)

echo.
echo Ambiente pronto!
echo.
echo Para ativar manualmente depois:
echo   .venv\Scripts\activate
echo.
echo Para abrir o notebook:
echo   jupyter notebook note.ipynb
echo.
pause