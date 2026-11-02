# Clipboard helpers shared by the wrapper scripts (sourced, not executed).
# macOS: pbcopy/pbpaste without a UTF-8 locale read and write the clipboard in a legacy encoding,
# which garbles any non-ASCII text, so the locale is forced.

clip_copy() {
  if command -v pbcopy >/dev/null; then LANG=en_US.UTF-8 pbcopy
  elif command -v wl-copy >/dev/null; then wl-copy
  elif command -v xclip >/dev/null; then xclip -selection clipboard
  elif command -v xsel >/dev/null; then xsel --clipboard --input
  elif command -v clip.exe >/dev/null; then clip.exe
  else echo "No clipboard tool found (pbcopy, wl-copy, xclip, xsel, clip.exe)" >&2; return 1
  fi
}

clip_paste() {
  if command -v pbpaste >/dev/null; then LANG=en_US.UTF-8 pbpaste
  elif command -v wl-paste >/dev/null; then wl-paste --no-newline
  elif command -v xclip >/dev/null; then xclip -selection clipboard -o
  elif command -v xsel >/dev/null; then xsel --clipboard --output
  elif command -v powershell.exe >/dev/null; then powershell.exe -NoProfile -Command Get-Clipboard | tr -d '\r'
  else echo "No clipboard tool found (pbpaste, wl-paste, xclip, xsel, powershell.exe)" >&2; return 1
  fi
}
