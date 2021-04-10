# About

HubGrep is a search engine for public code repositories. It searches through a list of code hosting services such as Gitlab or Github and presents matching results to you.

With HubGrep it is less important where projects are hosted - all sources are treated equally when presenting results to you.

HubGrep is free software - we encourage you to host your own search instance, with your own set of code hosters!

You can find the open-source code [on Github](https://github.com/HubGrep/hubgrep_search).
  
If you are hosting projects yourself, consider [adding your instance to our list]({{ url_for('security.login') }}) - HubGrep currently support Gitea, Gitlab, and Github! 

Something missing? Open a pull requests or [create an issue](https://github.com/HubGrep/hubgrep_search/issues/new) for us!


## Funded from March 2021 until August 2021 by

<p style="display: flex; flex-direction: row; justify-content: center; align-items: center;">
    <a href="https://www.bmbf.de/en/" rel="nofollow">
        <img src="{{ url_for('static', filename='images/logos/bmbf_de.jpg') }}" alt="Logo of the German Ministry for Education and Research" style="max-width:100%; padding:20px;" height="150px">
    </a>
    <a href="https://prototypefund.de/en/" rel="nofollow">
        <img src="{{ url_for('static', filename='images/logos/prototype_fund.svg') }}" alt="Logo of the Prototype Fund" style="max-width:100%; padding:20px;" height="150px">
    </a>
</p>
