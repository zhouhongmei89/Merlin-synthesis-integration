set current_path=%cd%

%current_path%\tool\1_labelGeneration\merlinstatalign.exe %current_path%\input\LabelGeneratorSettings.config

python %current_path%\tool\2_reorgFiles\reorg_singing_files.py -c  %current_path%\input\reorg-singing-files.yaml

python %current_path%\tool\3_linguisticExtraction\src\linguisticExtraction.py %current_path%\input\linguisticExtraction.conf

%current_path%\tool\4_decode\tool\ConvertFormatDecode.exe %current_path%\input\Settings.config

python %current_path%\tool\5_wavGeneration\src\WavGeneration.py %current_path%\input\WavGeneration.conf

xcopy /y %current_path%\intermediate\5_wavGeneration\output\*.wav %current_path%\output