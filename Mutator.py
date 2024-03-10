class Mutator:

    def __init__(self) -> None:
        self.mutators = [
            self.flip_bit,
            self.flip_bit_general,
            self.flip_bit_2,
            self.flip_bit_4,
            self.flip_byte
            ]
        
    def flip_bit(self, num: int, n: int) -> int:
        # Flips the nth bit of the given number.
        # Parameters:
        # num (int): The number whose bit is to be flipped.
        # n (int): The position of the bit to flip (0-indexed from the right).
        # Returns:
        # int: The number with the nth bit flipped.
        # Create a mask with the nth bit set to 1
        mask = 1 << n  
        # XOR the number with the mask to flip the nth bit
        return num ^ mask  
    
    def flip_bit_general(self,num: int, n: int, k:int, stepover:int) -> int:
        num= "{0:b}".format(num)
        binary_list = list(num)
        i = n-1  # start from the nth bit (indexing starts from 0)
        while i < (len(binary_list)):
            for j in range(i, min(i + k, len(binary_list))):
                if binary_list[j] == '0':
                    binary_list[j] = '1' 
                elif binary_list[j]=='1':
                    binary_list[j] = '0'
            i += k+stepover
        return int(''.join(binary_list), 2)
    
    def flip_bit_2(self,num: int) ->int:
        return self.flip_bit_general(self,num,1,2,1)
    
    def flip_bit_4(self,num: int) ->int:
        return self.flip_bit_general(self,num,1,4,1)
    
    def flip_byte(self,num: int) ->int:
        return self.flip_bit_general(self,num,1,8,8)
