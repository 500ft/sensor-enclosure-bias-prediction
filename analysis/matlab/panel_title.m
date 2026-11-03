function panel_title(ax, letter, label, S)
%PANEL_TITLE Left-aligned bold panel letter, optionally followed by a short panel label.
%   The letter is 10 pt bold; the label is 8 pt. MATLAB's LaTeX interpreter
%   rejects \small and \footnotesize but accepts \fontsize{..}{..}\selectfont.
%   Labels name the panel's subject; findings belong in the caption file.
if nargin < 3 || strlength(label) == 0
    str = sprintf('\\textbf{%s}', letter);
else
    str = sprintf('\\textbf{%s}\\enspace{\\fontsize{%d}{%d}\\selectfont %s}', letter, S.size.note, ...
        S.size.note + 2, label);
end
title(ax, str, 'Interpreter', 'latex', 'FontSize', S.size.letter, 'Color', S.c.ink, ...
    'FontWeight', 'normal');
ax.TitleHorizontalAlignment = 'left';
end
