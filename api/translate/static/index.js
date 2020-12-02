const LOCALE = 'zh';
const DEFAULT_TYPES = [
  {
    label: '自动',
    value: 'auto'
  },
  {
    label: '中文',
    value: 'zh'
  },
  {
    label: '英文',
    value: 'en'
  }
];

const LANG_CN_MESSAGES = {
  title: '翻译',
  lang: '语言',
  language: 'English | 中文',
  message: {
    content: '翻译内容',
    language: '翻译语言',
    placeholder: '请输入内容',
    result: '翻译结果',
    validator: '请输入需要翻译的内容'
  },
  button: { submit: '提交', reset: '清空' }
};

const LANG_EN_MESSAGES = {
  title: 'Translate',
  lang: 'Language',
  language: '中文 | English',
  message: {
    content: 'Translate content',
    language: 'Translate language',
    placeholder: 'Please enter content here',
    result: 'Response results',
    validator: 'Please enter the content to be translated'
  },
  button: { submit: 'Submit', reset: 'Reset' }
};

// @ts-ignore
new Vue({
  // @ts-ignore
  i18n: new VueI18n({
    locale: LOCALE,
    messages: { en: LANG_EN_MESSAGES, zh: LANG_CN_MESSAGES }
  }),
  el: '#app',
  data() {
    return {
      lang: LOCALE,
      types: DEFAULT_TYPES,
      toTypes: DEFAULT_TYPES.slice(1),
      result: undefined,
      rules: {
        postData: [
          {
            validator: (rule, value, callback) => {
              if (!value) {
                callback(this.$t('message.validator'));
              } else {
                callback();
              }
            },
            trigger: 'input'
          }
        ]
      },
      form: {
        to: DEFAULT_TYPES[1].value,
        from: DEFAULT_TYPES[0].value,
        postData: undefined
      }
    };
  },

  created() {
    this.fetchTypes();
  },
  methods: {
    toggle() {
      const { from, to } = this.form;

      if (from === 'auto') {
        this.$message.error('无法自动识别翻译对象');
      } else if (from === to) {
        this.$message.error('此举毫无意义');
      } else {
        this.form.from = to;
        this.form.to = from;
      }
    },
    toggleLanguage(lang) {
      if (lang !== this.lang) {
        this.lang = lang;
        this.$i18n.locale = lang;
        this.fetchTypes(lang);
      }
    },
    reset() {
      this.$refs.form.resetFields();
      this.result = undefined;
    },
    async fetchApi(url, body) {
      const response = await fetch(`/api/${url}`, {
        method: 'POST',
        headers: {
          'content-type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      return response.json();
    },
    animation(
      to = document.documentElement.offsetHeight - document.documentElement.clientHeight,
      count = document.documentElement.scrollTop
    ) {
      window.scrollTo(0, (count += Math.ceil((to - count) / 2)));
      requestAnimationFrame(() => (document.documentElement.scrollTop >= to ? false : this.animation(to, count)));
    },
    submit() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          const { from, to } = this.form;

          if (from === to) {
            this.$message.error('此举毫无意义');
          } else {
            const loading = this.$loading({
              fullscreen: false,
              look: false,
              text: 'Loading'
            });

            try {
              const { result } = await this.fetchApi('post/translate', {
                q: this.form.postData,
                from: from,
                to: to
              });

              this.result = result.trans_result[0].dst;
              loading.close();

              this.$message.success('翻译成功！');
              this.$nextTick(this.animation);
            } catch (error) {
              loading.close();
              this.$message.error('提交失败！');
            }
          }
        } else {
          return false;
        }
      });
    },
    async fetchTypes(lang) {
      try {
        const types = await this.fetchApi('fetch/types', { lang });

        this.types = types;
        this.toTypes = types.filter(({ value }) => value !== 'auto');
        this.form.from = types[0].value;
        this.form.to = types[1].value;
      } catch (error) {
        console.log(error);
        this.$message.error('获取翻译对象失败，请尝试刷新页面重试');
      }
    }
  }
});
