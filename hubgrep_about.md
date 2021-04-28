# About

HubGrep is a search engine for public code repositories. It searches through a list of code hosting services such as Gitlab or Github and presents matching results to you.

With HubGrep it is less important where projects are hosted - all sources are treated equally when presenting results to you.

HubGrep is free software - we encourage you to host your own search instance, with your own set of code hosters!

You can find our open-source code [here](https://github.com/HubGrep/hubgrep_search).
  
If you are hosting projects yourself, consider [adding your instance to our list]({{ url_for('security.login') }}) - HubGrep currently support Gitea, Gitlab, and Github! 

Something missing? Open a pull request or [create an issue](https://github.com/HubGrep/hubgrep_search/issues/new) for us!

<div class="hubgrep-fund-logos">
    <p>Funded from March 2021 until August 2021 by</p>
    <div>    
        <a class="bmbf" href="https://www.bmbf.de/en/" rel="nofollow">
            <img src="{{ url_for('static', filename='images/logos/bmbf_en.jpg') }}" alt="Logo of the German Ministry for Education and Research">
        </a>
        <a href="https://prototypefund.de/en/" rel="nofollow">
            <img src="{{ url_for('static', filename='images/logos/prototype_fund.svg') }}" alt="Logo of the Prototype Fund">
        </a>
    </div>
</div>
