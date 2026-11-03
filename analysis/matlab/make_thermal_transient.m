function make_thermal_transient(root, outDir, S)
%MAKE_THERMAL_TRANSIENT Weather forcing above one temperature-bias panel per variant.
%   Input: analysis/figures/data/thermal_transient_series.csv, written by
%   `python -m analysis.thermal_transient`. It holds every fifth 1-min step of
%   the retained period: solar (hourly mean held over the preceding hour), 10 m
%   wind, and each variant's 5th, 50th and 95th percentile bias over 400 draws.
%   Output: thermal_transient_prediction.pdf (vector) and .png (300 dpi).

T = readtable(fullfile(root, 'analysis', 'figures', 'data', 'thermal_transient_series.csv'), ...
    'TextType', 'string');
t = datetime(T.utc, 'InputFormat', 'yyyy-MM-dd''T''HH:mm', 'TimeZone', 'UTC');
x = days(t - datetime(2026, 8, 31, 'TimeZone', 'UTC'));   % day of September 2026, UTC
ids = ["V0", "V0P", "V1", "V2"];
names = ["Baseline closed box (V0)", "Painted closed-box control (V0P)", ...
         "Passive multi-plate shield (V1)", "Actively aspirated reference (V2)"];
band = 0.78 + 0.22 * S.c.blue;          % light blue, a region rather than a series colour
bandText = 0.3 * band + 0.7 * S.c.blue;    % darker than the band, for its label
xl = [floor(min(x) * 24) / 24, ceil(max(x) * 24) / 24];
ticks = 4:2:14;
tickLabels = arrayfun(@(d) sprintf('Sep %d', d), ticks, 'UniformOutput', false);

fig = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 18 20]);
tl = tiledlayout(fig, 6, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
axs = gobjects(6, 1);

axs(1) = nexttile(tl); hold(axs(1), 'on');
stairs(axs(1), x(1:end-1), T.ghi_w_m2(2:end), '-', 'Color', S.c.ink, 'LineWidth', 0.7);
set(axs(1), 'YLim', [0 900], 'YTick', 0:400:800);
ylabel(axs(1), 'Solar (W/m$^2$)');
panel_title(axs(1), 'a', 'hourly mean solar irradiance', S);

axs(2) = nexttile(tl); hold(axs(2), 'on');
plot(axs(2), x, T.wind10_m_s, '-', 'Color', S.c.ink, 'LineWidth', 0.7);
set(axs(2), 'YLim', [0 6], 'YTick', 0:2:6);
ylabel(axs(2), 'Wind at 10 m (m/s)');
panel_title(axs(2), 'b', 'wind speed', S);

for i = 1:4
    ax = nexttile(tl); axs(2 + i) = ax; hold(ax, 'on');
    lo = T.(ids(i) + "_p05_degc"); mid = T.(ids(i) + "_p50_degc"); hi = T.(ids(i) + "_p95_degc");
    fill(ax, [x; flipud(x)], [lo; flipud(hi)], band, 'EdgeColor', 'none');
    yline(ax, 0, ':', 'Color', S.c.grey, 'LineWidth', 0.8);
    plot(ax, x, mid, '-', 'Color', S.c.blue, 'LineWidth', 0.9);
    set(ax, 'YLim', [-4 17], 'YTick', 0:5:15);
    ylabel(ax, 'Bias ($^\circ$C)');
    panel_title(ax, char('b' + i), names(i), S);
end
% labels once, in the flattest panel
ax = axs(6);
text(ax, xl(2) - 0.05, 16.5, 'median of the input draws', 'Color', S.c.blue, ...
    'FontSize', S.size.note, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top');
text(ax, xl(2) - 0.05, 12.0, 'shaded: 5th to 95th percentile', 'Color', bandText, ...
    'FontSize', S.size.note, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top');
text(ax, xl(1) + 0.05, -0.7, 'zero', 'Color', S.c.grey, 'FontSize', S.size.note, ...
    'HorizontalAlignment', 'left', 'VerticalAlignment', 'top');

for k = 1:6
    set(axs(k), 'XLim', xl, 'XTick', ticks);
    if k < 6, axs(k).XTickLabel = {}; else, axs(k).XTickLabel = tickLabels; end
end
xlabel(axs(6), 'Date in 2026 (UTC)');
linkaxes(axs, 'x');
export_pair(fig, fullfile(outDir, 'thermal_transient_prediction'));
end
