from PIL import Image, ImageDraw, ImageFont
import traceback

class ScorecardGenerator:
    def __init__(self, scorecard_image_path):
        self.scorecard_image_path = scorecard_image_path

    def generate_scorecard(self, data: dict, output_image_path: str, grp_img: str, winner):
        try:
            scorecard_image = Image.open(self.scorecard_image_path)

            font = ImageFont.truetype('Assets/ARIALBLACKITALIC.TTF', 48)
            text_color = "darkslategray"

            draw = ImageDraw.Draw(scorecard_image)

            # Write the text on the image
            self._draw_text(draw, font, text_color, (44, 538), data['Team A']['best_batsman']['player_id'])
            self._draw_text(draw, font, text_color, (564, 538), data['Team B']['best_batsman']['player_id'])
            self._draw_text(draw, font, text_color, (44, 876), data['Team A']['best_bowler']['player_id'])
            self._draw_text(draw, font, text_color, (564, 876), data['Team B']['best_bowler']['player_id'])

            font = ImageFont.truetype('Assets/ARIALBD 1.TTF', 50)

            self.write_stats(data, draw, font)

            font = ImageFont.truetype('Assets/ARIALBD 1.TTF', 45)

            # Write the team scores on image
            self._draw_text(draw, font, "darkgrey", (32, 97), f"Score: {data['Team A']['score']}")
            self._draw_text(draw, font, "blue", (28, 93), f"Score: {data['Team A']['score']}")
            self._draw_text(draw, font, "darkgrey", (672, 97), f"Score: {data['Team B']['score']}")
            self._draw_text(draw, font, "blue", (668, 93), f"Score: {data['Team B']['score']}")
            self._draw_text(draw, font, "darkgrey", (44, 159), f"in {data['Team A']['overs']}")
            self._draw_text(draw, font, "blue", (40, 155), f"in {data['Team A']['overs']}")
            self._draw_text(draw, font, "darkgrey", (798, 159), f"in {data['Team B']['overs']}")
            self._draw_text(draw, font, "blue", (794, 155), f"in {data['Team B']['overs']}")

            font = ImageFont.truetype('Assets/BungeeTint-Regular.ttf', 50)
            win_text = f'Team {winner} won the match !!' if not winner == 'Tie' else 'This match was a Tie !!'
            self._draw_text(draw, font, "red", (155, 1160), win_text)
            self._draw_text(draw, font, "teal", (155, 1164), win_text)

            scorecard_image.save(output_image_path)

            self._add_profile_picture(grp_img, output_image_path)
        except Exception as e:
            # print error
            print(f'An error occured while handling generate_scorecard')
            print(e)
            traceback.print_exc()

    def _draw_text(self, draw, font, fill, coordinates, text):
        draw.text(coordinates, text, font=font, fill=fill)

    def write_stats(self, data, draw, font):
        # team a batting
        self._draw_text(draw, font, "black", (25, 675), str(data['Team A']['best_batsman']['runs']))
        self._draw_text(draw, font, "black", (130, 675), str(data['Team A']['best_batsman']['balls']))
        self._draw_text(draw, font, "black", (230, 675), str(data['Team A']['best_batsman']['sixes']))
        self._draw_text(draw, font, "black", (352, 675), str(data['Team A']['best_batsman']['fours']))
        # team b batting
        self._draw_text(draw, font, "black", (559, 675), str(data['Team B']['best_batsman']['runs']))
        self._draw_text(draw, font, "black", (658, 675), str(data['Team B']['best_batsman']['balls']))
        self._draw_text(draw, font, "black", (759, 675), str(data['Team B']['best_batsman']['sixes']))
        self._draw_text(draw, font, "black", (878, 675), str(data['Team B']['best_batsman']['fours']))
        # team a bowling
        self._draw_text(draw, font, "black", (25, 1005), str(data['Team A']['best_bowler']['overs']))
        self._draw_text(draw, font, "black", (130, 1005), str(data['Team A']['best_bowler']['runs_given']))
        self._draw_text(draw, font, "black", (247, 1005), str(data['Team A']['best_bowler']['wickets']))
        self._draw_text(draw, font, "black", (351, 1005), str(data['Team A']['best_bowler']['extra']))

        # team b bowling
        self._draw_text(draw, font, "black", (559, 1005), str(data['Team B']['best_bowler']['overs']))
        self._draw_text(draw, font, "black", (658, 1005), str(data['Team B']['best_bowler']['runs_given']))
        self._draw_text(draw, font, "black", (777, 1005), str(data['Team B']['best_bowler']['wickets']))
        self._draw_text(draw, font, "black", (878, 1005), str(data['Team B']['best_bowler']['extra']))


    def _add_profile_picture(self, grp_img, output_image_path):
        # Open the group profile image
        img = Image.open(grp_img)

        width, height = img.size
        radius = min(width, height) // 2

        # Crop the image into a circle
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((width//2-radius, height//2-radius, width//2+radius, height//2+radius), fill=255)
        img.putalpha(mask)

        target_radius = 120
        img.thumbnail((target_radius*2, target_radius*2))

        # Open the background image
        bg_img = Image.open(output_image_path)
        x, y = (bg_img.size[0] - img.size[0]) // 2, (bg_img.size[1] - img.size[1]) // 2
        bg_img.paste(img, (365, 45), img)

        bg_img.save(output_image_path)


# if __name__ == "__main__":
    # scorecard_generator = ScorecardGenerator('Assets\scorecard.jpg')    
    data = {
    'Team A': {
        'score': "112/4",
        'overs': "12.2",
        'best_bowler': {
            'player_id': 'player1',
            'overs': 5.3,
            'wickets': 8,
            'runs_given': 150, 
            "extra": 4
        },
        'best_batsman': {
            'player_id': 'player3',
            'runs': 350,
            'balls': 91,
            'sixes': 5,
            'fours': 15
        }
    },
    'Team B': {
        'score': "98/10",
        'overs': "9.3",
        'best_bowler': {
            'player_id': 'player5',
            'overs': 7,
            'wickets': 9,
            'runs_given': 12, 
            "extra": 2
        },
        'best_batsman': {
            'player_id': 'player2',
            'runs': 400,
            'balls': 92,
            'sixes': 6,
            'fours': 18
        }
    },
    'winner': 'A'
}
    # scorecard_generator.generate_scorecard(data, 'output.jpg', 'Assets\profile pic.jpg')