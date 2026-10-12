from pathlib import Path


class MockImageGenerator:
    def __init__(self, root=".cozy-data/mock-images"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def generate(self,payload):
        target=self.root/f'p{payload["book_position"]}-s{payload["scene_number"]:02}.txt'
        target.write_text(f'MOCK IMAGE\n{payload["title"]}\n',encoding="utf-8")
        return str(target)


class MockVisualReviewer:
    def review(self,image_path,brief):
        return {"result":"PASS","reason":"mock reviewer pass"}
