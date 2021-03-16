new Vue({
  el: '#app',
  data: {
    songs: [],
    search: undefined,
    isFind: false,
    album: undefined,
    author: undefined,
    name: undefined,
    songSrc: undefined,
    albumPicture: undefined,
    authorPicture: undefined,
    progress: 0,
    currentTime: 0,
    duration: 0,
    lrcTextList: [],
    isPlaying: false,
    showSlider: false,
    loopPlay: true,
    showLrcIndex: 0
  },
  computed: {
    barCurrentTime() {
      return this.getTime(this.currentTime);
    },
    barDurationTime() {
      return this.getTime(this.duration);
    }
  },
  mounted() {
    const audioElm = this.$refs.musicPlay;
    audioElm.addEventListener('canplay', () => {
      this.play();
    });
    audioElm.addEventListener(
      'timeupdate',
      _.throttle(() => {
        if (!this.lock) {
          this.currentTime = parseInt(audioElm.currentTime);
        }
        if (audioElm.readyState > 0) {
          this.duration = parseInt(audioElm.duration);
          this.progress = (this.currentTime / this.duration) * 100;
        }
        if (this.duration === this.currentTime) {
          if (this.loopPlay) {
            setTimeout(() => {
              this.play();
            }, 500);
          } else {
            this.isPlaying = false;
          }
        }
        const re = new RegExp(`\\[${this.barCurrentTime}.[\\d\\.]+\\]([^\\[\\]\\d]+)\\[`);
        if (re.test(this.lrcText)) {
          if (this.lrcTextList.indexOf(re.exec(this.lrcText)[1]) > -1) {
            const el = this.$refs.lrcBox.$el;
            this.showLrcIndex = this.lrcTextList.indexOf(re.exec(this.lrcText)[1]);
            const scrollTop = parseInt(el.querySelectorAll('p')[this.showLrcIndex].offsetTop - el.offsetHeight / 2);
            if (scrollTop > 0) {
              $(el).animate({ scrollTop }, 300);
            }
          }
        }
      }, 300)
    );
  },
  methods: {
    async fetch(url, key) {
      if (localStorage.getItem(url + key)) {
        return JSON.parse(localStorage.getItem(url + key));
      } else {
        const res = await fetch(`${url}/${key}`, {
          method: 'POST'
        });
        const data = await res.json();
        if (!data.error) {
          localStorage.setItem(url + key, JSON.stringify(data));
          return data;
        }
        return [];
      }
    },
    getTime(time) {
      const start = parseInt(time / 60) > 9 ? parseInt(time / 60) : '0' + parseInt(time / 60);
      const end = parseInt(time % 60) > 9 ? parseInt(time % 60) : '0' + parseInt(time % 60);
      return start + ':' + end;
    },
    async querySearch(queryString, cb) {
      cb(await this.fetch('find', queryString || '周杰伦'));
    },
    onSelect(item) {
      this.isFind = true;
      this.album = item.album;
      this.name = item.name;
      this.author = item.author;
      this.albumPicture = item.albumPicture;
      this.authorPicture = item.authorPictur;
      this.songSrc = item.src;
      this.songId = item.id;
      this.fetchLRC();
    },
    play() {
      this.$refs.musicPlay.play();
      this.isPlaying = true;
    },
    pause() {
      this.$refs.musicPlay.pause();
      this.isPlaying = false;
    },
    async fetchLRC() {
      this.lrcTextList = [];
      if (this.songId) {
        try {
          const findTitleRE = /\[ti:(.+?)\]/g;
          const findAuthorRE = /\[ar:(.+?)\]/g;
          const parseLyricRE = /\]([^\[\]]+)\[/g;
          const data = await this.fetch('select', this.songId);
          const title = findTitleRE.exec(data.lrcText);
          const author = findAuthorRE.exec(data.lrcText);
          this.lrcText = data.lrcText;
          this.lrcTextList.push(
            title[1],
            author[1],
            ...data.lrcText.match(parseLyricRE).map(str => str.slice(1, str.length - 1))
          );
        } catch (error) {
          this.lrcTextList = ['解析失败, 暂无歌词~'];
        }
      }
    },
    setHeight() {
      this.$refs.lrcBox.$el.style.height = this.$refs.albumPicture.$el.offsetHeight + 'px';
    },
    handleChange(val) {
      if (val !== this.$refs.musicPlay.currentTime) {
        const oldCurrentTime = this.$refs.musicPlay.currentTime;
        this.lock = true;
        this.$nextTick(() => {
          this.$refs.musicPlay.currentTime = val;
          this.currentTime = val;
          this.lock = false;
          if (oldCurrentTime >= this.duration) {
            this.play();
          }
        });
      }
    },
    download() {
      const loading = this.$loading({
        lock: true,
        text: '解析下载链接中...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      fetch('/download/' + this.songId, { mode: 'no-cors' })
        .then(res => res.blob())
        .then(blob => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.download = this.name + '.mp3';
          a.href = url;
          document.body.appendChild(a);
          a.click();
          a.remove();
          loading.close();
        });
    }
  }
});
