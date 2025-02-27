from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = ['routes', 'template_manager', 'data_manager']

# Collect data files
datas = collect_data_files('templates') + collect_data_files('static')