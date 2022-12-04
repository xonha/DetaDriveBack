# Deta Drive
2018003703 - Henrique Castro Oliveira  
2019011989 - Luiz Fernando Rezende  
2019005186 - Camila Grande de Freitas  
2019009096 - Laís Nascimento  

# Links
https://www.detadrive.tk/
https://api.detadrive.tk/

# Dependências
## Node
### Instalação Node
1. Para fazer download do node é só acessar o site https://nodejs.org.
1. Após o download, basta clicar no executável e seguir o passo-a-passo do próprio executável para instalar o Node.

### Testando a Instalação
1. Para verificar se a instalação foi feita com sucesso, podemos testar pelo prompt de comando se temos o Node instalado na nossa máquina.
1. No menu procure por ``prompt de comando`` e abra o aplicativo.
1. Dentro do aplicativo digite ``node -v`` e aperte Enter.
1. No resultado do comando deve aparecer qual a versão atual do node instalado em seu computador.

### Instalar Yarn
No nosso projeto utilizamos o yarn para instalar os pacotes utilizados no desenvolvimento. Para instalar o yarn precisamos abrir novamente o prompt de comando e executar o seguinte comando:
``npm install --global yarn``

## Python
Para Windows, é recomendada a instalação do Python versão 3.8 ou mais recente, seguindo os seguintes passos:
1. Visitar o site oficial para download https://www.python.org/downloads/.
1. Na aba downloads, no menu superior, clicar em “Download Python 3.x.x”.
1. Depois de baixado, executar o arquivo, clicando sobre ele.
1. Na janela que se abre, marcar a caixa de seleção ``Add Python 3.8 to PATH``.
1. Selecionar a opção ``Install now``.

## Git
1. Faça o download no site official https://git-scm.com/download/win.
1. Execute o instalador.
1. No terminal executar ``git --version``

## Deta
1. Entrar/Criar conta no site https://www.deta.sh/.
1. Clicar em ``Dashboard`` e ``Sign Up/Sign In``.
1. No Dashboard, navegar até ``Project Keys`` e clicar em ``Create Key``.
1. Salvar a ``Project Key`` em um local seguro.

# Ambiente Local
## Front-End
### Clonar o repositório
1. Navegar pelo terminal até a pasta que deseja salvar o projeto.
1. Executar ``git clone https://github.com/camilagfreitas01/DetaDrive``.

### Rodar o projeto
1. Pelo terminal, na mesma pasta do projeto, executar o comando ``yarn``.
1. Com as dependências instaladas ``yarn start``.
1. Uma página web com o endereço http://localhost:3000/.

## Back-End
### Clonar o repositório
1. Navegar pelo terminal até a pasta que deseja salvar o projeto.
1. Executar ``git clone https://github.com/henoliveira/DetaDrive``.

### Rodar o projeto
1. pip install -r requirements.txt
1. pip install -r requirements_dev.txt
1. No diretório do projeto criar um arquivo .env
1. No arquivo .env criar a variável de ambiente DETA_PROJECT_KEY como chave, o valor deve ser a ``Project Key`` obtida no passo ``Deta``.
1. No mesmo diretório executar ``uvicorn main:app --host 0.0.0.0 --port 80000``.
1. Uma página web com o endereço http://localhost:8000/.

# Ambiente Nuvem
## Deta CLI

## Windows
1. ``iwr https://get.deta.dev/cli.ps1 -useb | iex``
1. Executar ``deta login``.

### Mac/Linux
1. ``curl -fsSL https://get.deta.dev/cli.sh | sh``
1. No linux é necessário adicionar o binário "deta" ao PATH https://linuxize.com/post/how-to-add-directory-to-path-in-linux/.
1. Executar ``deta login``.

## Deploy Back-End
1. Com a variável de ambiente ``DETA_PROJECT_KEY``.
1. Com o Deta CLI configurado.
1. Navegar pelo terminal até ao diretório do projeto.
1. Executar ``deta deploy``.

## Deploy Front-End
1. Criar uma conta no site da Vercel https://vercel.com/.
1. Conectar no repositório.
1. Escolher o projeto a fazer o deploy.
1. Escolher o nome do projeto.
1. Clicar em ``Deploy``.
