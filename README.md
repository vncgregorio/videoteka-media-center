# Videoteka Media Center

Um centro de mídia desktop moderno para Linux com interface estilo streaming.

## Características

- 🎬 Interface estilo streaming (Netflix, Amazon Prime, etc.)
- 📁 Suporte para vídeos, áudios, imagens e documentos PDF
- 🖼️ Geração automática de thumbnails
- ⌨️ Navegação completa por teclado
- 🔊 Preview de áudio (30 segundos)
- 📄 Visualização de primeira página de PDFs
- 💾 Banco de dados SQLite portável
- 🎨 Tema escuro moderno

## Requisitos

- Python 3.9 ou superior
- Qt6 (PySide6)
- Bibliotecas Python (veja requirements.txt)
- **Dependências do sistema** (necessárias para Qt 6.5+):
  - `libxcb-cursor0` ou `libxcb-cursor1` (dependendo da distribuição)
  - Outras dependências xcb (geralmente já instaladas)

## Instalação

### Desenvolvimento

1. Clone o repositório:
```bash
git clone https://github.com/videoteka/media-center.git
cd media-center
```

2. Instale as dependências do sistema (necessárias para Qt 6.5+):
```bash
# Ubuntu/Debian/Linux Mint
sudo apt update
sudo apt install libxcb-cursor0 libxcb-xinerama0 libxcb-xfixes0 libxcb-render0 libxcb-shape0

# Fedora/RHEL/CentOS
sudo dnf install libxcb-cursor libxcb-xinerama libxcb-xfixes libxcb-render libxcb-shape

# Arch Linux
sudo pacman -S libxcb-cursor libxcb-xinerama libxcb-xfixes libxcb-render libxcb-shape
```

**Nota**: Se `libxcb-cursor0` não estiver disponível na sua distribuição, tente `libxcb-cursor1` ou apenas `libxcb-cursor`.

3. Crie um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

4. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

5. Execute a aplicação:
```bash
python -m src.main
```

### Empacotamento

#### AppImage

Para criar um AppImage:

```bash
cd packaging/appimage
appimage-builder --recipe AppImageBuilder.yml
```

O AppImage será gerado no diretório de build.

#### Flatpak

Para criar um Flatpak:

```bash
cd packaging/flatpak
flatpak-builder build org.videoteka.MediaCenter.yml
flatpak-builder --run build org.videoteka.MediaCenter.yml videoteka
```

## Uso

### Primeira Execução

Na primeira execução, a aplicação mostrará um assistente de configuração onde você pode:

1. Selecionar as pastas que contêm seus arquivos multimídia
2. Confirmar e iniciar o escaneamento
3. Aguardar o processamento dos arquivos

### Navegação

- **Setas**: Navegar entre os cards de mídia
- **Enter**: Abrir o arquivo selecionado com o aplicativo padrão
- **Esc**: Fechar previews/diálogos
- **Home/End**: Ir para o primeiro/último item
- **Filtros**: Use os botões na barra lateral para filtrar por tipo

### Filtros

- **Todos**: Mostra todos os arquivos
- **Vídeos**: Apenas arquivos de vídeo
- **Áudios**: Apenas arquivos de áudio
- **Imagens**: Apenas imagens
- **Documentos**: Apenas PDFs

Use a barra de busca para encontrar arquivos por nome.

## Formatos Suportados

### Vídeo
- MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, 3GP

### Áudio
- MP3, FLAC, WAV, OGG, M4A, AAC, WMA, Opus, AMR

### Imagem
- JPG, JPEG, PNG, GIF, BMP, WebP, SVG, TIFF, ICO

### Documento
- PDF

## Estrutura do Projeto

```
videoteka-media-center/
├── src/
│   ├── main.py              # Ponto de entrada
│   ├── models/              # Modelos de dados
│   ├── views/               # Componentes de UI
│   ├── controllers/         # Controladores
│   ├── utils/               # Utilitários
│   └── resources/           # Recursos (estilos, ícones)
├── tests/                   # Testes unitários
├── packaging/               # Configurações de empacotamento
├── data/                    # Dados da aplicação (SQLite, thumbnails)
└── requirements.txt        # Dependências Python
```

## Desenvolvimento

### Executar Testes

```bash
python -m pytest tests/
```

### Contribuir

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Versionamento

Este projeto segue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

Versão atual: **0.1.0**

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Roadmap

- [ ] Suporte a playlists
- [ ] Metadados avançados (IMDB para filmes, tags)
- [ ] Busca avançada
- [ ] Organização automática
- [ ] Suporte a streaming de rede
- [ ] Temas personalizáveis
- [ ] Suporte a legendas
- [ ] Player de mídia integrado

## Suporte

Para reportar bugs ou solicitar funcionalidades, abra uma issue no GitHub.

## Autores

- Videoteka Team

## Agradecimentos

- PySide6 pela excelente biblioteca Qt
- Comunidade open source


