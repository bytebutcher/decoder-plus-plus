import uuid


class Model:

    def __init__(self):
        self._tabs = []
        self._current_tab_number = 1

    def add_tab(self, name=None) -> 'core.TabModel':
        tab = TabModel(uuid.uuid4().hex, name)
        self._tabs.append(tab)
        return tab

    def close_tab(self, index, name):
        self._tabs.pop(index)

    def move_tab(self, from_index, to_index):
        self._tabs.insert(to_index, self._tabs.pop(from_index))

    def rename_tab(self, index, old_name, new_name):
        self._tabs[index].name = new_name


class TabModel:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self._frames = []

    def new_frame(self, index):
        self._frames.append()

    def previous(self, id):
        frame = self.get_frame_by_id(id)
        index = self._frames.index(frame)
        return self._frames[index - 1]

    def has_previous(self, id):
        frame = self.get_frame_by_id(id)
        return frame is not None and self._frames.index(frame) > 0

    def next(self, id):
        frame = self.get_frame_by_id(id)
        index = self._frames.index(frame)
        return self._frames[index + 1]

    def has_next(self, id):
        frame = self.get_frame_by_id(id)
        if frame is None:
            return False
        index = self._frames.index(frame)
        return len(self._frames) > 1 and index < (len(self._frames) - 1)

    def move_down(self, id):
        frame = self.get_frame_by_id(id)
        next_frame = self.next(id)
        self.swap_frames(self._frames.index(frame), self._frames.index(next_frame))
        return next_frame

    def move_up(self, id):
        frame = self.get_frame_by_id(id)
        previous_frame = self.previous(id)
        self.swap_frames(self._frames.index(frame), self._frames.index(previous_frame))
        return frame

    def close_frame(self, id):
        frame = self.get_frame_by_id(id)
        if frame:
            self._frames.remove(frame)

    def get_frame_by_id(self, id):
        for frame in self._frames:
            if frame.id == id:
                return frame

    def swap_frames(self, index1, index2):
        self._frames[index1], self._frames[index2] = self._frames[index2], self._frames[index1]


class FrameModel:

    def __init__(self, parent_tab, id, codec, text, error):
        self.id = id
        self.codec = codec
        self.text = text
        self.error = error

    def execute(self, input):
        try:
            self.text = self.codec.run(input)
            self.error = None
        except BaseException as err:
            self.error = err.message # TODO: incorrect
            raise err
        return self.text

    def get_line_numbers(self):
        pass

    def get_characters(self):
        pass
