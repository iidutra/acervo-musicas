(function () {
  'use strict';

  var CHORD_REGEX = /^[A-G][#b]?(m|dim|aug|sus[24]?|maj)?[0-9]?(\/[A-G][#b]?)?$/;

  function isChordToken(token) {
    return CHORD_REGEX.test(token.trim());
  }

  function isChordLine(line) {
    if (!line || !line.trim()) return false;
    var tokens = line.trim().split(/\s+/);
    return tokens.length > 0 && tokens.every(isChordToken);
  }

  function parseCifraTexto(text) {
    if (!text) return [];
    var lines = text.replace(/\r\n/g, '\n').split('\n');
    var result = [];
    var i = 0;
    while (i < lines.length) {
      if (isChordLine(lines[i])) {
        var chordLine = lines[i];
        var lyricsLine = (i + 1 < lines.length && !isChordLine(lines[i + 1])) ? lines[i + 1] : '';
        var chords = extractChordsFromLine(chordLine);
        result.push({ chords: chords, lyrics: lyricsLine });
        i += lyricsLine !== '' ? 2 : 1;
      } else {
        result.push({ chords: [], lyrics: lines[i] });
        i++;
      }
    }
    return result;
  }

  function extractChordsFromLine(line) {
    var chords = [];
    var re = /\S+/g;
    var match;
    while ((match = re.exec(line)) !== null) {
      chords.push({ pos: match.index, name: match[0] });
    }
    return chords;
  }

  function buildChordLine(chords, minLength) {
    var length = minLength || 0;
    chords.forEach(function (c) {
      var end = c.pos + c.name.length;
      if (end > length) length = end;
    });
    var arr = new Array(length + 1).join(' ').split('');
    chords.slice().sort(function (a, b) { return a.pos - b.pos; }).forEach(function (c) {
      for (var j = 0; j < c.name.length; j++) {
        var idx = c.pos + j;
        while (arr.length <= idx) arr.push(' ');
        arr[idx] = c.name[j];
      }
    });
    return arr.join('');
  }

  function buildCifraTexto(data) {
    var lines = [];
    data.forEach(function (entry) {
      var chordStr = '';
      if (entry.chords && entry.chords.length > 0) {
        chordStr = buildChordLine(entry.chords, entry.lyrics.length);
      }
      if (chordStr.trim()) {
        lines.push(chordStr);
      }
      lines.push(entry.lyrics);
    });
    return lines.join('\n');
  }

  // ---- Styles injected once ----
  var STYLE_ID = 'cifra-editor-styles';
  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    var css = [
      '.cifra-editor { font-family: "Courier New", monospace; font-size: 14px; line-height: 1.4; }',
      '.cifra-editor * { box-sizing: border-box; }',
      '.cifra-editor-tabs { display: flex; gap: 0; margin-bottom: 8px; border-bottom: 2px solid #e5e7eb; }',
      '.cifra-editor-tab { padding: 6px 18px; cursor: pointer; border: none; background: none; font-family: inherit; font-size: 13px; font-weight: 600; color: #6b7280; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: color 0.15s, border-color 0.15s; }',
      '.cifra-editor-tab:hover { color: #4f46e5; }',
      '.cifra-editor-tab.active { color: #4f46e5; border-bottom-color: #4f46e5; }',
      '.cifra-editor-visual { padding: 4px 0; }',
      '.cifra-line-group { margin-bottom: 4px; }',
      '.cifra-chord-rail { position: relative; min-height: 1.2em; border-bottom: 1px dotted #d1d5db; cursor: text; user-select: none; -webkit-user-select: none; white-space: pre; }',
      '.cifra-chord-rail:hover { background: rgba(79, 70, 229, 0.04); }',
      '.cifra-lyrics-line { white-space: pre; color: #1f2937; min-height: 1.2em; padding: 0; }',
      '.cifra-chord { position: absolute; top: 0; font-weight: 700; color: #4f46e5; cursor: pointer; white-space: nowrap; line-height: 1.4; padding: 0 1px; border-radius: 2px; transition: background 0.12s; }',
      '.cifra-chord:hover { background: rgba(79, 70, 229, 0.12); }',
      '.cifra-chord.selected { background: rgba(79, 70, 229, 0.18); }',
      '.cifra-chord-delete { display: none; position: absolute; top: -4px; right: -8px; width: 14px; height: 14px; line-height: 14px; text-align: center; font-size: 10px; font-weight: 700; color: #fff; background: #ef4444; border-radius: 50%; cursor: pointer; z-index: 2; }',
      '.cifra-chord:hover .cifra-chord-delete { display: block; }',
      '.cifra-chord-input { position: absolute; top: 0; background: transparent; border: none; border-bottom: 2px solid #4f46e5; outline: none; font-family: "Courier New", monospace; font-size: 14px; font-weight: 700; color: #4f46e5; padding: 0; width: 60px; line-height: 1.4; z-index: 5; }',
      '.cifra-textarea-wrap { padding: 0; }',
      '.cifra-textarea-wrap textarea { width: 100%; min-height: 300px; font-family: "Courier New", monospace; font-size: 14px; line-height: 1.4; border: 1px solid #d1d5db; border-radius: 4px; padding: 8px; color: #1f2937; resize: vertical; outline: none; }',
      '.cifra-textarea-wrap textarea:focus { border-color: #4f46e5; box-shadow: 0 0 0 2px rgba(79,70,229,0.15); }'
    ].join('\n');
    var style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ---- Measure character width ----
  function measureCharWidth(container) {
    var span = document.createElement('span');
    span.style.fontFamily = '"Courier New", monospace';
    span.style.fontSize = '14px';
    span.style.visibility = 'hidden';
    span.style.position = 'absolute';
    span.style.whiteSpace = 'pre';
    span.textContent = 'MMMMMMMMMM';
    container.appendChild(span);
    var w = span.offsetWidth / 10;
    container.removeChild(span);
    return w || 8.4;
  }

  // ---- CifraEditor class ----
  function CifraEditor(options) {
    this.container = options.container;
    this.onUpdate = options.onUpdate || function () {};
    this.data = []; // array of { chords: [{pos, name}], lyrics: string }
    this.mode = 'visual'; // 'visual' | 'texto'
    this._charWidth = 0;
    this._els = {};
    this._destroyed = false;

    injectStyles();
    this._build();

    if (options.cifraTexto) {
      this.importCifra(options.cifraTexto);
    } else if (options.lyrics) {
      this._initFromLyrics(options.lyrics);
    }
    this._render();
  }

  CifraEditor.prototype._initFromLyrics = function (lyrics) {
    var lines = lyrics.replace(/\r\n/g, '\n').split('\n');
    this.data = lines.map(function (l) {
      return { chords: [], lyrics: l };
    });
  };

  CifraEditor.prototype._build = function () {
    var self = this;
    var root = document.createElement('div');
    root.className = 'cifra-editor';

    // Tabs
    var tabsBar = document.createElement('div');
    tabsBar.className = 'cifra-editor-tabs';

    var tabVisual = document.createElement('button');
    tabVisual.type = 'button';
    tabVisual.className = 'cifra-editor-tab active';
    tabVisual.textContent = 'Visual';
    tabVisual.addEventListener('click', function () { self._switchMode('visual'); });

    var tabTexto = document.createElement('button');
    tabTexto.type = 'button';
    tabTexto.className = 'cifra-editor-tab';
    tabTexto.textContent = 'Texto';
    tabTexto.addEventListener('click', function () { self._switchMode('texto'); });

    tabsBar.appendChild(tabVisual);
    tabsBar.appendChild(tabTexto);

    // Visual panel
    var visualPanel = document.createElement('div');
    visualPanel.className = 'cifra-editor-visual';

    // Texto panel
    var textoPanel = document.createElement('div');
    textoPanel.className = 'cifra-textarea-wrap';
    textoPanel.style.display = 'none';
    var textarea = document.createElement('textarea');
    textarea.spellcheck = false;
    textarea.addEventListener('input', function () {
      self._textoDirty = true;
    });
    textoPanel.appendChild(textarea);

    root.appendChild(tabsBar);
    root.appendChild(visualPanel);
    root.appendChild(textoPanel);

    this.container.innerHTML = '';
    this.container.appendChild(root);

    this._els.root = root;
    this._els.tabVisual = tabVisual;
    this._els.tabTexto = tabTexto;
    this._els.visualPanel = visualPanel;
    this._els.textoPanel = textoPanel;
    this._els.textarea = textarea;

    this._charWidth = measureCharWidth(root);
  };

  CifraEditor.prototype._switchMode = function (mode) {
    if (mode === this.mode) return;

    if (this.mode === 'texto' && this._textoDirty) {
      // Sync textarea back to data
      this.data = parseCifraTexto(this._els.textarea.value);
      this._textoDirty = false;
      this._notify();
    }

    if (this.mode === 'visual') {
      // Data is already up-to-date from visual interactions
    }

    this.mode = mode;

    if (mode === 'visual') {
      this._els.tabVisual.classList.add('active');
      this._els.tabTexto.classList.remove('active');
      this._els.visualPanel.style.display = '';
      this._els.textoPanel.style.display = 'none';
      this._render();
    } else {
      this._els.tabTexto.classList.add('active');
      this._els.tabVisual.classList.remove('active');
      this._els.visualPanel.style.display = 'none';
      this._els.textoPanel.style.display = '';
      this._els.textarea.value = buildCifraTexto(this.data);
      this._textoDirty = false;
    }
  };

  CifraEditor.prototype._render = function () {
    var self = this;
    var panel = this._els.visualPanel;
    panel.innerHTML = '';

    if (!this.data.length) return;

    // Re-measure in case font has loaded
    this._charWidth = measureCharWidth(this._els.root);

    this.data.forEach(function (entry, lineIdx) {
      var group = document.createElement('div');
      group.className = 'cifra-line-group';

      // Chord rail
      var rail = document.createElement('div');
      rail.className = 'cifra-chord-rail';
      rail.dataset.line = lineIdx;

      // Render existing chords
      self._renderChords(rail, lineIdx);

      // Click on rail to add chord
      rail.addEventListener('mousedown', function (e) {
        if (e.target !== rail) return; // clicked on a chord element, not rail
        e.preventDefault();
        var rect = rail.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var charPos = Math.round(x / self._charWidth);
        if (charPos < 0) charPos = 0;
        self._openInput(rail, lineIdx, charPos, null);
      });

      // Lyrics line
      var lyrLine = document.createElement('div');
      lyrLine.className = 'cifra-lyrics-line';
      lyrLine.textContent = entry.lyrics || '\u00a0';

      group.appendChild(rail);
      group.appendChild(lyrLine);
      panel.appendChild(group);
    });
  };

  CifraEditor.prototype._renderChords = function (rail, lineIdx) {
    var self = this;
    var entry = this.data[lineIdx];
    if (!entry || !entry.chords) return;

    entry.chords.forEach(function (chord, chordIdx) {
      var span = document.createElement('span');
      span.className = 'cifra-chord';
      span.textContent = chord.name;
      span.style.left = (chord.pos * self._charWidth) + 'px';

      // Delete button
      var del = document.createElement('span');
      del.className = 'cifra-chord-delete';
      del.textContent = '\u00d7';
      del.addEventListener('mousedown', function (e) {
        e.stopPropagation();
        e.preventDefault();
        self.data[lineIdx].chords.splice(chordIdx, 1);
        self._notify();
        self._render();
      });
      span.appendChild(del);

      // Click to edit
      span.addEventListener('mousedown', function (e) {
        if (e.target === del) return;
        e.stopPropagation();
        e.preventDefault();
        span.classList.add('selected');
        self._openInput(rail, lineIdx, chord.pos, chordIdx);
      });

      rail.appendChild(span);
    });
  };

  CifraEditor.prototype._openInput = function (rail, lineIdx, charPos, editIdx) {
    var self = this;

    // Remove any existing input
    var old = rail.querySelector('.cifra-chord-input');
    if (old) old.remove();

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'cifra-chord-input';
    input.style.left = (charPos * this._charWidth) + 'px';

    if (editIdx !== null && editIdx !== undefined) {
      input.value = this.data[lineIdx].chords[editIdx].name;
      input.select();
    }

    rail.appendChild(input);

    // Use setTimeout to ensure the input is in DOM before focus
    setTimeout(function () { input.focus(); input.select(); }, 0);

    var confirmed = false;

    function confirm() {
      if (confirmed) return;
      confirmed = true;
      var val = input.value.trim();
      input.remove();

      if (!val) {
        // If editing and cleared, delete the chord
        if (editIdx !== null && editIdx !== undefined) {
          self.data[lineIdx].chords.splice(editIdx, 1);
          self._notify();
          self._render();
        }
        return;
      }

      if (editIdx !== null && editIdx !== undefined) {
        self.data[lineIdx].chords[editIdx].name = val;
        self.data[lineIdx].chords[editIdx].pos = charPos;
      } else {
        self.data[lineIdx].chords.push({ pos: charPos, name: val });
      }

      // Sort chords by position
      self.data[lineIdx].chords.sort(function (a, b) { return a.pos - b.pos; });
      self._notify();
      self._render();
    }

    function cancel() {
      if (confirmed) return;
      confirmed = true;
      input.remove();
      self._render();
    }

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        confirm();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        cancel();
      }
    });

    input.addEventListener('blur', function () {
      // Small delay to allow click events to fire first
      setTimeout(function () {
        if (!confirmed) confirm();
      }, 120);
    });
  };

  CifraEditor.prototype._notify = function () {
    if (this._destroyed) return;
    try {
      this.onUpdate(this.getCifraTexto());
    } catch (e) {
      // silently ignore callback errors
    }
  };

  CifraEditor.prototype.getCifraTexto = function () {
    if (this.mode === 'texto' && this._textoDirty) {
      return this._els.textarea.value;
    }
    return buildCifraTexto(this.data);
  };

  CifraEditor.prototype.getLetra = function () {
    return this.data.map(function (e) { return e.lyrics; }).join('\n');
  };

  CifraEditor.prototype.importCifra = function (text) {
    this.data = parseCifraTexto(text);
    this._textoDirty = false;
    if (this.mode === 'visual') {
      this._render();
    } else {
      this._els.textarea.value = text;
    }
    this._notify();
  };

  CifraEditor.prototype.destroy = function () {
    this._destroyed = true;
    if (this._els.root && this._els.root.parentNode) {
      this._els.root.parentNode.removeChild(this._els.root);
    }
    this._els = {};
    this.data = [];
    this.onUpdate = function () {};
  };

  // Expose to window
  window.CifraEditor = CifraEditor;
  window.parseCifraTexto = parseCifraTexto;

})();
