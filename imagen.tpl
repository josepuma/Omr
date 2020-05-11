<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/uikit/3.2.3/css/uikit.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/uikit/3.2.3/js/uikit.min.js"></script>
<style>
    .contenedor{
        width: 100%;
        padding: 5px;
    }
    .col-6{
        width: 50%;
        padding: 5px;
    }
    .img-hoja{
        position:relative;
        float: left;
    }
</style>

    <div class="uk-child-width-1-4@m uk-padding-small" uk-grid>
        <div class="uk-card uk-card-default">
            <div class="uk-card-media-top">
                <img class="img-hoja" src="/static/1_original_Image.jpg" alt="">
            </div>
            <div class="uk-card-body">
                <h3 class="uk-card-title">Imagen Original</h3>
                <p>Imagen Original, enviada desde la aplicación móvil</p>
            </div>
        </div>
    

        <div class="uk-card uk-card-default">
            <div class="uk-card-media-top">
                <img class="img-hoja" src="/static/bordes.jpg" alt="">
            </div>
            <div class="uk-card-body">
                <h3 class="uk-card-title">Imagen Bordes</h3>
                <p>Imagen con filtro Canny que permite detectar los bordes de la hoja de respuesta</p>
            </div>
        </div>
    </div>
