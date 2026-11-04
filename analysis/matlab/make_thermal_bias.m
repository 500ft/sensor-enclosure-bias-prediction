function make_thermal_bias(root, outDir, S)
%MAKE_THERMAL_BIAS Steady temperature and RH bias against wind, one column per variant.
%   Input: analysis/figures/data/thermal_bias_sweep.csv, written by
%   `python analysis/thermal_bias.py`. The plotted values are checked against
%   the committed analysis/output/thermal_bias_table.csv before drawing.
%   Output: thermal_bias.pdf (vector) and thermal_bias.png (300 dpi).
%   Blue solid = 1000 W/m^2, orange dashed = 800 W/m^2, labelled in panel (e).

T = readtable(fullfile(root, 'analysis', 'figures', 'data', 'thermal_bias_sweep.csv'), ...
    'TextType', 'string');
tablePath = fullfile(root, 'analysis', 'output', 'thermal_bias_table.csv');
opts = detectImportOptions(tablePath, 'CommentStyle', '#');
opts = setvartype(opts, {'variant_id', 'variant_name'}, 'string');
R = readtable(tablePath, opts);
for k = 1:height(R)
    m = T.variant_id == R.variant_id(k) & T.g_w_m2 == R.g_w_m2(k) & abs(T.wind_m_s - R.wind_m_s(k)) < 1e-9;
    assert(nnz(m) == 1, 'sweep lacks table row %d', k);
    assert(abs(T.delta_t_degc(m) - R.delta_t_degc(k)) <= 5e-5 && abs(T.rh_err_pct(m) - R.rh_err_pct(k)) <= 5e-5, ...
        'sweep disagrees with thermal_bias_table.csv at row %d', k);
end

ids = ["V0", "V0P", "V1", "V2"];
names = {{'Baseline', 'closed box (V0)'}, {'Painted closed-box', 'control (V0P)'}, ...
         {'Passive multi-plate', 'shield (V1)'}, {'Actively aspirated', 'reference (V2)'}};
G = [1000 800];
col = {S.c.blue, S.c.orange};
sty = {'-', '--'};
quantity = {'delta_t_degc', 'rh_err_pct'};
ylims = {[-1.5 24.5], [-37 3]};
yticks = {0:5:20, -30:10:0};
ylabels = {{'Sensor minus air', 'temperature ($^\circ$C)'}, {'Reported minus true', 'RH (percentage points)'}};
letters = 'abcdefgh';

fig = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 18 10.5]);
tl = tiledlayout(fig, 2, 4, 'TileSpacing', 'compact', 'Padding', 'compact');
for r = 1:2
    for c = 1:4
        ax = nexttile(tl); hold(ax, 'on');
        yline(ax, 0, ':', 'Color', S.c.grey, 'LineWidth', 0.8);
        for j = 1:2
            m = T.variant_id == ids(c) & T.g_w_m2 == G(j);
            plot(ax, T.wind_m_s(m), T.(quantity{r})(m), sty{j}, 'Color', col{j}, 'LineWidth', 1.4);
        end
        set(ax, 'XLim', [-0.12 5.12], 'XTick', 0:5, 'YLim', ylims{r}, 'YTick', yticks{r});
        if c > 1, ax.YTickLabel = {}; else, ylabel(ax, ylabels{r}); end
        if r == 1, ax.XTickLabel = {}; end
        panel_title(ax, letters((r - 1) * 4 + c), '', S);
        if r == 1
            text(ax, 4.95, ylims{1}(2) - 0.6, names{c}, 'HorizontalAlignment', 'right', ...
                'VerticalAlignment', 'top', 'FontSize', S.size.note, 'Color', S.c.ink);
        end
        if r == 1 && c == 1
            text(ax, 4.95, 0.45, 'zero', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom', ...
                'FontSize', S.size.note, 'Color', S.c.grey);
        end
        if r == 2 && c == 1
            % direct series labels over x = 2.8..5: orange above its curve, blue below its curve
            m8 = T.variant_id == "V0" & T.g_w_m2 == 800 & T.wind_m_s >= 2.8;
            m10 = T.variant_id == "V0" & T.g_w_m2 == 1000 & T.wind_m_s >= 2.8;
            yo = max(T.rh_err_pct(m8));
            yb = min(T.rh_err_pct(m10));
            text(ax, 4.95, yo + 1.8, '800 W/m$^2$', 'Color', S.c.orange, 'FontSize', S.size.label, ...
                'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
            text(ax, 4.95, yb - 1.8, '1000 W/m$^2$', 'Color', S.c.blue, 'FontSize', S.size.label, ...
                'HorizontalAlignment', 'right', 'VerticalAlignment', 'top');
        end
    end
end
xlabel(tl, 'External wind speed (m/s)', 'Interpreter', 'latex', 'FontSize', S.size.label, 'Color', S.c.ink);
export_pair(fig, fullfile(outDir, 'thermal_bias'));
end
