function render_figures(root, outDir)
%RENDER_FIGURES Draw this repository's data figures and result-table fragments.
%   From the repository root, after the Python steps in README.md have written
%   the plot data:
%       matlab -batch "addpath('analysis/matlab'); render_figures"
%   root defaults to the repository that contains this file; outDir defaults
%   to analysis/figures. Figures go to outDir as name.pdf + name.png (300 dpi);
%   LaTeX table fragments go to outDir/tables. Each output runs in its own
%   try/catch, and the call fails at the end if any output failed.

if nargin < 1 || isempty(root)
    root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
end
if nargin < 2 || isempty(outDir)
    outDir = fullfile(root, 'analysis', 'figures');
end
tableDir = fullfile(outDir, 'tables');
if ~isfolder(tableDir), mkdir(tableDir); end
dataDir = fullfile(root, 'analysis', 'output');

S = fig_style();
jobs = {
    'thermal_bias',                       @() make_thermal_bias(root, outDir, S)
    'thermal_transient_prediction',       @() make_thermal_transient(root, outDir, S)
    'synthetic_identifiability_profiles', @() make_identifiability_profiles(root, outDir, S, ...
        'synthetic_identifiability', 'identifiability_design.json')
    'synthetic_identifiability_tradeoffs', @() make_identifiability_tradeoffs(root, outDir, S, ...
        'synthetic_identifiability', 'identifiability_design.json')
    'synthetic_identifiability_60s_profiles', @() make_identifiability_profiles(root, outDir, S, ...
        'synthetic_identifiability_60s', 'identifiability_design_60s.json')
    'synthetic_identifiability_60s_tradeoffs', @() make_identifiability_tradeoffs(root, outDir, S, ...
        'synthetic_identifiability_60s', 'identifiability_design_60s.json')
    'predicted_rise_table',               @() make_rise_table(dataDir, tableDir)
    'result_tables',                      @() make_result_tables(dataDir, tableDir)
    };
failed = 0;
fprintf('%s\n', version);
for k = 1:size(jobs, 1)
    try
        jobs{k, 2}();
        fprintf('[ok] %s\n', jobs{k, 1});
    catch err
        failed = failed + 1;
        fprintf('[failed] %s: %s\n', jobs{k, 1}, getReport(err, 'extended', 'hyperlinks', 'off'));
        close all force
    end
end
if failed
    error('render_figures:failed', '%d of %d outputs failed', failed, size(jobs, 1));
end
end
