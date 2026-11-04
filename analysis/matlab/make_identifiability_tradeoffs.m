function make_identifiability_tradeoffs(root, outDir, S, stem, cfgName)
%MAKE_IDENTIFIABILITY_TRADEOFFS Gain-set openness and coverage by record length and schedule.
%   Inputs: the committed analysis/output/<stem>.csv (one row per cell) and
%   analysis/input/<cfgName>; defaults 'synthetic_identifiability' and
%   'identifiability_design.json'. Top row: matched
%   dynamics, fraction of gain sets at the search edge. Bottom row: ambient
%   excursion, fraction of gain sets containing the true eta/G. Single step is
%   blue with filled circles; repeated steps orange with hollow squares, so a
%   tie shows as a ring around a dot. Output: <stem>_tradeoffs.pdf/.png.

if nargin < 4 || isempty(stem), stem = 'synthetic_identifiability'; end
if nargin < 5 || isempty(cfgName), cfgName = 'identifiability_design.json'; end
R = readtable(fullfile(root, 'analysis', 'output', [stem '.csv']), 'TextType', 'string');
cfg = jsondecode(fileread(fullfile(root, 'analysis', 'input', cfgName)));
tau = cfg.tau_s(:)';
sch = string(fieldnames(cfg.schedules))';     % registration order: single_step, repeated_steps
assert(isequal(sch, ["single_step", "repeated_steps"]), 'unexpected schedule order');
rows = {"matched", 'gain_open_fraction'; "ambient_mismatch", 'gain_coverage'};
col = {S.c.blue, S.c.orange};
sty = {'-o', '--s'};
msz = [4.5 6.5];
face = {S.c.blue, 'none'};
hours = cfg.duration_s(:)' / 3600;

fig = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 18 10.5]);
tl = tiledlayout(fig, 2, numel(tau), 'TileSpacing', 'compact', 'Padding', 'compact');
for r = 1:2
    for c = 1:numel(tau)
        ax = nexttile(tl); hold(ax, 'on');
        if r == 2
            yline(ax, cfg.profile_level, ':', 'Color', S.c.grey, 'LineWidth', 0.8);
        end
        for j = 1:2
            m = R.scenario == rows{r, 1} & R.tau_s == tau(c) & R.schedule == sch(j);
            [d, order] = sort(R.duration_s(m));
            v = R.(rows{r, 2})(m);
            plot(ax, d / 3600, v(order), sty{j}, 'Color', col{j}, 'LineWidth', 1.2, ...
                'MarkerSize', msz(j), 'MarkerFaceColor', face{j}, 'MarkerEdgeColor', col{j});
        end
        set(ax, 'XScale', 'log', 'XLim', [0.4 8], 'XTick', hours, ...
            'XTickLabel', arrayfun(@(h) sprintf('%.3g', h), hours, 'UniformOutput', false), ...
            'XMinorTick', 'off', 'YLim', [-0.04 1.04], 'YTick', 0:0.2:1);
        if c > 1, ax.YTickLabel = {}; end
        if r == 1, ax.XTickLabel = {}; end
        if r == 1
            panel_title(ax, char('a' + c - 1), sprintf('generating $C/G = %g$ min', tau(c) / 60), S);
        else
            panel_title(ax, char('a' + numel(tau) + c - 1), '', S);
        end
        if r == 1 && c == numel(tau)
            text(ax, 2.3, 0.86, 'repeated steps', 'Color', S.c.orange, 'FontSize', S.size.label, ...
                'VerticalAlignment', 'bottom');
            text(ax, 0.55, 0.42, 'single step', 'Color', S.c.blue, 'FontSize', S.size.label, ...
                'VerticalAlignment', 'top');
        end
        if r == 2 && c == 1
            text(ax, 7.6, cfg.profile_level - 0.03, sprintf('nominal %g\\%%', 100 * cfg.profile_level), ...
                'Color', S.c.grey, 'FontSize', S.size.note, 'HorizontalAlignment', 'right', ...
                'VerticalAlignment', 'top');
        end
    end
end
ylabel(nexttile(tl, 1), {'Gain sets at search', 'edge (fraction)'});
ylabel(nexttile(tl, numel(tau) + 1), {'Gain sets containing', 'true $\eta/G$ (fraction)'});
xlabel(tl, 'Observation duration (h)', 'Interpreter', 'latex', 'FontSize', S.size.label, 'Color', S.c.ink);
export_pair(fig, fullfile(outDir, [stem '_tradeoffs']));
end
