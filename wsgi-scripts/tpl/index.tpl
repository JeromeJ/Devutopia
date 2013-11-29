<!DOCTYPE html>
<html>
	<head>
		<title>Hello world ☺ - Olissea DEV</title>
		<meta charset="UTF-8" />
		<link rel="stylesheet" media="screen" type="text/css" title="Main style" href="css/main.css" />
	</head>
	<body>
		<header id="header">
			<div id="status"><strong><span class="WIP">WIP</span> Work In Progress</strong>, <em>come back later!</em></div><!-- # TODO: Remove that? When? -->
			<div id="extra"><em>Contact me if interested!</em><br /><strong>Contact:</strong> e-warning [at symbol] hotmail.com</div><!-- # TODO: See tag:devutopia.net,2013-11-03:Topic-changing-contact-info (in helloworld.py) -->
			<div id="title"><strong><span class="dev">Dev</span><span class="utopia">utopia</span></strong></div>
		</header>

		<div id="main">
			<h1 id="catchphrase" >« A huge collaborative project to come! »</h1>
			<section class="spoiler">
				<h2>What is this?</h2>
				<ol id="moto">
					{moto}
				</ol>

				<p>
					So, your contributions will be automatically accepted under the "By users" tab and will be displayed to the whole world (if you wish), they'll stay there (if you wish), and, in case you proposed data for someone else's content and if you're lucky, it may get merged with the original content by his original author or be choosen to be the new official version.
				</p>
			</section>
			
			<section id="helloWorld">
				<h2>Hello World</h1>
				{langs}
				…<br />
				<button>Add a lang</button> <em>or</em> edit one… (<em>Not implemented yet… Soon!</em>)
			</section>

			
			<section id="test">
				<h2>Testing zone</h2>
				<p>
					{{test}}
				</p>
			</section>

		</div>

		<footer id="foot">
			<span id="privacyPolicy"> We don't collect data about you ☺<span class="heart">♥</span> → We <strong class="love">love</strong> you! <span class="hearts">❤💓💕💖💘💗💙💚💛💜💝💞💟💖💙💜💚💗💘💛💝💞💟</span><!-- # TODO: Ne s'affiche que sous win… Une piste: U+1F495, U+1F496, U+1F497, U+1F499, U+1F49A, U+1F49B, U+1F49C, U+1F49D, U+1F49E, U+1F49F, U+1F496, U+1F497, U+1F498, U+1F49B, U+1F49D, U+1F49E, U+1F49F la séquence complète. C’est valide, et il existe sûrement une fonte qui les a --><!-- Note for myself: If you edit that under windows, it will look glitched, don't edit that part!! --></span>
			<span id="source"><strong>Source:</strong> ftp://anonymous@devutopia.net/ </span>
		</footer>
	</body>
</html>