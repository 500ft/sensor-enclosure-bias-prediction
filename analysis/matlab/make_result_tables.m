function make_result_tables(dataDir, outDir)
%MAKE_RESULT_TABLES Write the steady result tables of thermal_bias_results.md as LaTeX.
%   Inputs: thermal_bias_table.csv and thermal_bias_night_table.csv in dataDir
%   (analysis/output). Outputs, booktabs + siunitx tabular fragments in outDir:
%     thermal_bias_temperature_table.tex  sensor minus air, four variants
%     thermal_bias_rh_table.tex           reported minus true RH, four variants
%     painted_control_table.tex           V0P rise, RH error and V0P - V1
%     night_table.tex                     clear-sky night case, G = 0
%   Every number is read from the CSVs; display precision matches the Markdown tables.

day = read_bias(fullfile(dataDir, 'thermal_bias_table.csv'));
night = read_bias(fullfile(dataDir, 'thermal_bias_night_table.csv'));
ids = ["V0", "V0P", "V1", "V2"];
heads = ["{\shortstack{Baseline closed\\box (V0)}}", "{\shortstack{Painted closed-box\\control (V0P)}}", ...
         "{\shortstack{Passive multi-plate\\shield (V1)}}", "{\shortstack{Actively aspirated\\reference (V2)}}"];
G = unique(day.g_w_m2)';
W = unique(day.wind_m_s)';
solarHead = "{\shortstack{Solar\\(\unit{\watt\per\square\metre})}}";
windHead = "{\shortstack{Wind\\(\unit{\metre\per\second})}}";
pick = @(T, id, g, w, col) T.(col)(T.variant_id == id & T.g_w_m2 == g & abs(T.wind_m_s - w) < 1e-9);

% Temperature and RH tables: one row per solar load and wind speed.
specs = {'delta_t_degc', 'Sensor minus air temperature (\unit{\degreeCelsius})', '2.1', 'thermal_bias_temperature_table.tex';
         'rh_err_pct', 'Reported minus true RH (percentage points)', '-2.1', 'thermal_bias_rh_table.tex'};
for s = 1:size(specs, 1)
    body = strings(0, 1);
    for g = G
        if ~isempty(body), body(end + 1, 1) = "\addlinespace"; end %#ok<AGROW>
        for w = W
            v = arrayfun(@(id) one(pick(day, id, g, w, specs{s, 1})), ids);
            lead = "";
            if w == W(1), lead = sprintf('%.0f', g); end
            body(end + 1, 1) = sprintf('%s & %.1f & %.1f & %.1f & %.1f & %.1f \\\\', lead, w, v); %#ok<AGROW>
        end
    end
    fmt = specs{s, 3};
    L = [header_comment(); ...
        sprintf("\\begin{tabular}{@{}S[table-format=4.0] S[table-format=1.1] *{4}{S[table-format=%s]}@{}}", fmt); ...
        "\toprule"; ...
        sprintf(" & & \\multicolumn{4}{c}{%s} \\\\", specs{s, 2}); ...
        "\cmidrule(l){3-6}"; ...
        solarHead + " & " + windHead + " & " + strjoin(heads, " & ") + " \\"; ...
        "\midrule"; body; "\bottomrule"; "\end{tabular}"];
    writelines(L, fullfile(outDir, specs{s, 4}));
end

% Painted-control table: V0P values and the difference of the exported rounded predictions.
body = strings(0, 1);
for g = G
    if ~isempty(body), body(end + 1, 1) = "\addlinespace"; end %#ok<AGROW>
    for w = W
        a = one(pick(day, "V0P", g, w, 'delta_t_degc'));
        b = one(pick(day, "V0P", g, w, 'rh_err_pct'));
        d = a - one(pick(day, "V1", g, w, 'delta_t_degc'));
        lead = "";
        if w == W(1), lead = sprintf('%.0f', g); end
        body(end + 1, 1) = sprintf('%s & %.1f & %.4f & %.4f & %.4f \\\\', lead, w, a, b, d); %#ok<AGROW>
    end
end
L = [header_comment(); ...
    "\begin{tabular}{@{}S[table-format=4.0] S[table-format=1.1] S[table-format=1.4] S[table-format=-2.4] S[table-format=1.4]@{}}"; ...
    "\toprule"; ...
    " & & \multicolumn{2}{c}{Painted box (V0P)} & {V0P $-$ V1} \\"; ...
    "\cmidrule(lr){3-4}\cmidrule(l){5-5}"; ...
    solarHead + " & " + windHead + " & {Rise (\unit{\degreeCelsius})} & {RH error (points)} & {\shortstack{painted box minus\\shield (\unit{\degreeCelsius})}} \\"; ...
    "\midrule"; body; "\bottomrule"; "\end{tabular}"];
writelines(L, fullfile(outDir, 'painted_control_table.tex'));

% Night table: calm and 5 m/s for the baseline box, calm only for the shield and aspirated reference.
rows = strings(0, 1);
nm = ["Baseline closed box (V0)", "Passive multi-plate shield (V1)", "Actively aspirated reference (V2)"];
nid = ["V0", "V1", "V2"];
for i = 1:3
    calm = one(pick(night, nid(i), 0, 0, 'delta_t_degc'));
    rh = one(pick(night, nid(i), 0, 0, 'rh_err_pct'));
    if nid(i) == "V0"
        windy = sprintf('%.3f', one(pick(night, nid(i), 0, 5, 'delta_t_degc')));
    else
        windy = '{\textemdash}';
    end
    rows(end + 1, 1) = sprintf('%s & %.3f & %s & %+.2f \\\\', nm(i), calm, windy, rh); %#ok<AGROW>
end
L = [header_comment(); ...
    "\begin{tabular}{@{}l S[table-format=-1.3] S[table-format=-1.3] S[table-format=+2.2, retain-explicit-plus]@{}}"; ...
    "\toprule"; ...
    " & \multicolumn{2}{c}{Sensor minus air (\unit{\degreeCelsius})} & {RH error (points)} \\"; ...
    "\cmidrule(lr){2-3}\cmidrule(l){4-4}"; ...
    "Enclosure (variant) & {calm} & {\qty{5}{\metre\per\second}} & {calm} \\"; ...
    "\midrule"; rows; "\bottomrule"; "\end{tabular}"];
writelines(L, fullfile(outDir, 'night_table.tex'));
end

function T = read_bias(path)
opts = detectImportOptions(path, 'CommentStyle', '#');
opts = setvartype(opts, {'variant_id', 'variant_name'}, 'string');
T = readtable(path, opts);
end

function v = one(x)
assert(numel(x) == 1, 'expected exactly one CSV row');
v = x;
end

function s = header_comment()
s = "% Generated by make_result_tables.m from the committed thermal_bias CSVs; do not edit by hand.";
end
