// Building blocks: place each letter of the alphabet on one side of one of num_blocks blocks.
// Every block has num_sides sides, so it carries exactly num_sides letters, and the letters
// must be arranged so that every word in the list can be spelled by showing its letters one
// after another, each on a different block.
// dice[k] = the block that carries the k-th letter of the alphabet (0-based block index).

import org.jacop.constraints.Alldistinct;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int numBlocks = inst.getInt("num_blocks");     // number of blocks, from the instance
        int numSides = inst.getInt("num_sides");       // letters on each block
        int numLetters = inst.getInt("num_letters");   // one entry per letter of the alphabet
        String alphabet = inst.getString("alphabet");  // the letters, in order
        JSONArray words = inst.getJSONArray("words_str");

        // dice[k]: block carrying letter k of the alphabet
        IntVar[] dice = new IntVar[numLetters];
        for (int k = 0; k < numLetters; k++) {
            dice[k] = new IntVar(store, "dice" + k, 0, numBlocks - 1);
        }

        // inBlock[k][b] = 1 if letter k is on block b
        BooleanVar[][] inBlock = new BooleanVar[numLetters][numBlocks];
        for (int k = 0; k < numLetters; k++) {
            for (int b = 0; b < numBlocks; b++) {
                inBlock[k][b] = new BooleanVar(store, "on" + k + "_" + b);
                store.impose(new Reified(new XeqC(dice[k], b), inBlock[k][b]));
            }
        }

        // each block has exactly num_sides letters on it
        int[] ones = new int[numLetters];
        java.util.Arrays.fill(ones, 1);
        for (int b = 0; b < numBlocks; b++) {
            BooleanVar[] column = new BooleanVar[numLetters];
            for (int k = 0; k < numLetters; k++) column[k] = inBlock[k][b];
            store.impose(new LinearInt(column, ones, "==", numSides));
        }

        // each word: its letters are on pairwise different blocks, since the word is spelled
        // by turning the blocks one at a time and no block can show two of its letters
        for (int w = 0; w < words.length(); w++) {
            String word = words.getString(w);
            IntVar[] onBlocks = new IntVar[word.length()];
            for (int p = 0; p < word.length(); p++) {
                int k = alphabet.indexOf(word.charAt(p));
                onBlocks[p] = dice[k];
            }
            store.impose(new Alldistinct(onBlocks));
        }

        Model model = new Model().put("dice", dice);
        return model;
    }
}
