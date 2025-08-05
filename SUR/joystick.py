def page():
    return """<!DOCTYPE html>
            <html lang="en">

            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Surveillance Robot</title>
                <link rel="icon" type="image/x-icon" href="/favicon.png">
                <style>
                    body {
                        margin: 0;
                        font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                        background: linear-gradient(#b3a818, #ae691a);
                        background-repeat: no-repeat;
                        color: #e1c9c9;
                        text-align: center;
                        height: 100vh;
                        overflow: hidden;
                    }
                    
                    input[type="submit"] {
                        font-weight: 600;
                        font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
                        width: 115px;
                        height: 115px;
                        background-color: #af4c75;
                        border: none;
                        color: rgb(232, 197, 197);
                        text-shadow: 2px 3px 3px #472d05;
                        font-size: 15px;
                        cursor: pointer;
                        border-radius: 5px;
                        box-shadow: 0 8px 10px rgba(0, 0, 0, 0.26);
                        transition: transform 0.2s, box-shadow 0.2s;
                    }
                    
                    input[type="submit"]:hover {
                        color: #f3c6dd;
                        background-color: #ba5a9d;
                        transform: translateY(-6px);
                        box-shadow: 0 14px 16px rgba(0, 0, 0, 0.3);
                    }
                    
                    input {
                        width: 375px;
                        cursor: pointer;
                    }
                    
                    #speedValue,
                    #angleValue {
                        font-weight: bold;
                        color: #fec235;
                        text-shadow: 1px 1px 3px #472d05;
                    }
                    input[type="range"] {
                        width: 96%;
                        accent-color: rgb(153, 73, 24);
                    }
                    @media screen and (max-width: 400px) { 
                        input[type="submit"]{
                            width: 85px;
                            height: 70px;
                            font-size: 11px;
                        }
                        input[type="range"] {
                            zoom: 0.8;
                        }
                        body{
                            font-size: 12px;
                            line-height: 0px;
                        }
                    }
                    @media screen and (max-width: 387px) { 
                        input[type="submit"]{
                            width: 85px;
                            height: 70px;
                            font-size: 11px;
                        }
                        input[type="range"] {
                            zoom: 0.75;
                        }
                        body{
                            font-size: 12px;
                            line-height: 0px;
                        }
                    }
            </style>
            </head>

            <body>
                <center>
                    <b>
                        <table>
                            <tr>
                                <td>
                                    <form action="./forward_left">
                                        <input type="submit" value="Forward Left" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./forward">
                                        <input type="submit" value="Forward" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./forward_right">
                                        <input type="submit" value="Forward Right" />
                                    </form>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <form action="./left">
                                        <input type="submit" value="Left" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./stop">
                                        <input type="submit" value="Stop" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./right">
                                        <input type="submit" value="Right" />
                                    </form>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <form action="./backward_left">
                                        <input type="submit" value="Backward Left" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./back">
                                        <input type="submit" value="Back" />
                                    </form>
                                </td>
                                <td>
                                    <form action="./backward_right">
                                        <input type="submit" value="Backward Right" />
                                    </form>
                                </td>
                            </tr>
                        </table>
                        <p>Speed: <span id="speedValue">100</span> %</p>
                        <input type="range" min="0" max="100" value="100" class="slider" id="speedSlider">
                        <p>Camera Angle: <span id="angleValue">90</span> °</p>
                        <input type="range" min="0" max="180" value="90" class="slider" id="angleSlider">
                    </b>
                </center>
                <script>
                    // Angle slider functionality
                    var slider = document.getElementById('angleSlider');
                    var output = document.getElementById('angleValue');
                    slider.oninput = function () {
                        output.innerHTML = this.value;
                        fetch("/set?angle=" + this.value);
                    };

                    // Speed slider functionality
                    var sp_slider = document.getElementById('speedSlider');
                    var sp_output = document.getElementById('speedValue');
                    sp_slider.oninput = function () {
                        sp_output.innerHTML = this.value;
                        fetch("/set?speed=" + this.value);
                    };
                </script>
            </body>

            </html>
            """