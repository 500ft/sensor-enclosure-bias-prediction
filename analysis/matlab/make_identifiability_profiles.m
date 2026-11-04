function make_identifiability_profiles(root, outDir, S, stem, cfgName)
%MAKE_IDENTIFIABILITY_PROFILES Profile likelihood-ratio curves for the synthetic I1 study.
%   Input: analysis/figures/data/<stem>_profiles.csv, written by
%   `python -m analysis.render_identifiability` from the committed profile
%   arrays, and analysis/input/<cfgName> (cutoff, heater time constants, record
%   lengths). stem defaults to 'synthetic_identifiability' and cfgName to
%   'identifiability_design.json'; the 60 s cadence amendment passes
%   'synthetic_identifiability_60s' and 'identifiability_design_60s.json'. Three record lengths need three colours, so this
%   figure uses MATLAB default colours 1, 2 and 4 (colour 3, yellow, is too light
%   on white). Output: <stem>_profiles.pdf and .png.

if nargin < 4 || isempty(stem), stem = 'synthetic_identifiability'; end
if nargin < 5 || isempty(cfgName), cfgName = 'identifiability_design.json'; end
P = readtable(fullfile(root, 'analysis', 'figures', 'data', [stem '_profiles.csv']));
cfg = jsondecode(fileread(fullfile(root, 'analysis', 'input', cfgName)));
PROFILE_YMAX = 12;   % same value as render_identifiability.PROFILE_YMAX, quoted in the caption
scen = ["matched", "noisy", "ambient_mismatch", "probe_lag"];
labels = ["matched dynamics with quantization", "higher noise with coarser quantization", ...
          "an unobserved ambient excursion", "additional probe lag"];
C = lines(7);
col = {C(1, :), C(2, :), C(4, :)};
sty = {'-', '--', ':'};
lw = [1.3 1.3 1.6];
dur = cfg.duration_s(:)';
gen = max(cfg.tau_s) / 60;
cut = cfg.profile_delta_chi2;
x = P.candidate_cg_min;
% Direct-label anchors (candidate C/G in min, statistic): one row per record length,
% then the x anchor of the cutoff label in panel c. Placed clear of each run's curves.
lab = [0.6 2.3; 11 8; 140 10];
cutX = 0.55;
if strcmp(stem, 'synthetic_identifiability_60s')
    lab(3, :) = [250 10];
    cutX = 4;
end

fig = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 18 12]);
tl = tiledlayout(fig, 2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
for k = 1:4
    ax = nexttile(tl); hold(ax, 'on');
    yline(ax, cut, ':', 'Color', S.c.grey, 'LineWidth', 0.8);
    xline(ax, gen, '-.', 'Color', S.c.grey, 'LineWidth', 0.8);
    for j = 1:numel(dur)
        y = P.(sprintf('%s_%dmin', scen(k), dur(j) / 60));
        plot(ax, x, y, sty{j}, 'Color', col{j}, 'LineWidth', lw(j));
    end
    set(ax, 'XScale', 'log', 'XLim', [min(x) max(x)], 'YLim', [0 PROFILE_YMAX], ...
        'XTick', [1 10 100], 'XTickLabel', {'1', '10', '100'}, 'YTick', 0:4:12, 'Clipping', 'on');
    if mod(k, 2) == 0, ax.YTickLabel = {}; else, ylabel(ax, {'Profile likelihood-', 'ratio statistic'}); end
    if k <= 2, ax.XTickLabel = {}; end
    panel_title(ax, char('a' + k - 1), labels(k), S);
    if k == 1
        text(ax, lab(1, 1), lab(1, 2), sprintf('%.3g h', dur(1) / 3600), 'Color', col{1}, 'FontSize', S.size.label, ...
            'VerticalAlignment', 'bottom');
        text(ax, lab(2, 1), lab(2, 2), sprintf('%.3g h', dur(2) / 3600), 'Color', col{2}, 'FontSize', S.size.label, ...
            'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
        text(ax, lab(3, 1), lab(3, 2), sprintf('%.3g h', dur(3) / 3600), 'Color', col{3}, 'FontSize', S.size.label, ...
            'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle');
    end
    if k == 3
        text(ax, cutX, cut + 0.3, sprintf('nominal cutoff %.2f', cut), 'Color', S.c.grey, ...
            'FontSize', S.size.note, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
    end
    if k == 2
        % Two lines, right-aligned just inside the axes, so the label stays on the canvas.
        text(ax, max(x) / 1.03, PROFILE_YMAX - 0.4, {'generating $C/G$', sprintf('%g min', gen)}, ...
            'Color', S.c.grey, 'FontSize', S.size.note, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top');
    end
end
xlabel(tl, 'Candidate $C/G$ (min)', 'Interpreter', 'latex', 'FontSize', S.size.label, 'Color', S.c.ink);
export_pair(fig, fullfile(outDir, [stem '_profiles']));
end
