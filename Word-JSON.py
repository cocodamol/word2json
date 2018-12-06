from docx import Document
import glob
import json
import copy


class convert_file():
    def __init__(self, file, template, titles_list):
        self.file = file
        self.template = copy.deepcopy(template)
        self.out_file = file.replace(".docx",".json").replace("files", "jsons")
        self.titles_list = titles_list
        self.doc = Document(file)

    def gener(self, inner):
        length = len(inner)
        for i in range(length - 1):
            yield inner[i]

    def next_text(self):
        cur = next(self.gen)
        while len(cur.text) < 2:
            cur = next(self.gen)
        return cur

    def do_metadata(self, cur):
        if "data" in cur.text.lower() or "meta title" in cur.text.lower():
            cur = self.next_text()
            if "<meta title>" in cur.text:
                cur = self.next_text()
                self.template["title"] = cur.text
            else:
                self.template["title"] = cur.text
            cur = self.next_text()
            if "<meta description>" in cur.text or "meta data" in cur.text.lower():
                cur = self.next_text()
                self.template["metadescription"] = cur.text
            else:
                print("problem with meta data in file: " + str(self.file))

    def do_intro(self):
        cur = self.next_text()
        if "<h1>" in cur.text:
            heading = cur.text
            heading = heading.replace("<h1>", "").replace("</h1>", "")
            self.template["main_headline"].append({"type": "heading1", "content": {"text": heading, "spans": []}})
            cur = self.next_text()
            while "<h2>" not in cur.text and "<h3>" not in cur.text:
                self.template["preamble"].append({"type": "paragraph", "content": {"text": cur.text, "spans": []}})
                cur = self.next_text()
            return cur
        else:
            print("some heading issue: " + str(self.file))

    def do_paras(self, cur):
        if "<h2>" in cur.text or "<h3>" in cur.text:
            heading = cur.text
            heading = heading.replace("<h2>", "").replace("</h2>", "").replace("<h3>", "").replace("</h3>", "")
            title = next(self.titles)
            self.template[title].append({"type": "heading2", "content": {"text": heading, "spans": []}})
            cur = self.next_text()
            try:
                title = next(self.titles)
            except StopIteration:
                title = "why_play_text"
            while "<h2>" not in cur.text and "<h3>" not in cur.text:
                if title == "gameplay_text":
                    count = 0
                    for run in cur.runs:
                        if run.bold:
                            count = count + len(run.text)
                    if count > 0:
                        self.template[title].append({"type": "paragraph", "content": {"text": cur.text, "spans": [
                            {"start": 0, "end": count, "type": "strong"}]}})
                    else:
                        self.template[title].append({"type": "paragraph", "content": {"text": cur.text, "spans": []}})
                    cur = self.next_text()
                else:
                    self.template[title].append({"type": "paragraph", "content": {"text": cur.text, "spans": []}})
                    cur = self.next_text()
            try:
                self.do_paras(cur)
            except StopIteration:
                print("done")
        else:
            print("something wrong in the paragraphs: " + str(self.file))

    def control_flow(self):
        self.gen = self.gener(self.doc.paragraphs)
        self.titles = self.gener(self.titles_list)
        for cur in self.gen:
            self.do_metadata(cur)
            cur = self.next_text()
            if "on page" in cur.text.lower():
                cur = self.do_intro()
                self.do_paras(cur)
            break
        with open(self.out_file, "w") as f:
            f.write(json.dumps(self.template, ensure_ascii=False, indent=4))


json_template = {"type":"game","tags":[],"lang":"en-gb","grouplang":"W_2DjxIAAC4A84EU","main_headline":[],"preamble":[],
"how_to_win_title":[],"how_to_win_text":[],"winning_symbols_title":[],"symbols_images":[{}],"winning_symbols_text":[],
"gameplaytitle":[],"gameplay_text":[],"gameplayimages":[],"special_features_title":[],"special_features_text":[],
"jackpot_feature_title":[],"jackpot_feature_text":[],"payouts_and_wagering_limits_title":[],"payouts_and_wagering_limits_text":[],
"playing_on_mobile_title":[],"playing_on_mobile_text":[],"why_play_title":[],"why_play_text":[],"gameid":"","title":"","metadescription":""}

care_about_titles = ["how_to_win_title", "how_to_win_text", "winning_symbols_title", "winning_symbols_text", "gameplaytitle",
"gameplay_text", "special_features_title", "special_features_text", "jackpot_feature_title", "jackpot_feature_text",
"payouts_and_wagering_limits_title", "payouts_and_wagering_limits_text", "playing_on_mobile_title", "playing_on_mobile_text",
"why_play_title", "why_play_text"]

if __name__ == "__main__":
    dire = "files"
    direc = "./" + dire + "/*.docx"
    files = glob.glob(direc)
    for file in files:
        x = convert_file(file, json_template, care_about_titles)
        x.control_flow()
        print(x.template)

