import pickle
import pandas as pd

# Load up the resources we will need

print("Loading draft topic vectors.")
with open("../indexing/data/draft2topicvectors.pickle", "rb") as infile:
    draft2ldavec = pickle.load(infile)
print(len(draft2ldavec))


print("Loading draft tfidf vectors.")
# get tfidf representations for drafts
with open("../indexing/data/draft2tfidfvectors.pickle", "rb") as infile:
    draft2tfidfvec = pickle.load(infile)
print(len(draft2tfidfvec))


print("Loading candidate topic vectors.")
# get lda representations for candidates
with open("../indexing/data/pid2topicvectors.pickle", "rb") as infile:
    pid2ldavec = pickle.load(infile)
print(len(pid2ldavec))


print("Loading candidate tfidf vectors.")
# get tfidf representations for candidates
with open("../indexing/data/pid2tfidfvectors.pickle", "rb") as infile:
    pid2tfidfvec = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading draft2grouparea.")
# get tfidf representations for candidates
with open("../indexing/data/draft2grouparea.pickle", "rb") as infile:
    draft2grouparea = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading ml2activepids.")
# get tfidf representations for candidates
with open("../indexing/data/ml2activepids.pickle", "rb") as infile:
    ml2activepids = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading pid2areavectors.")
# get tfidf representations for candidates
with open("../indexing/data/pid2areavectors.pickle", "rb") as infile:
    pid2areavectors = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading pid2name.")
# get tfidf representations for candidates
with open("../indexing/data/pid2name.pickle", "rb") as infile:
    pid2name = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading pid2docsauthored.")
# get tfidf representations for candidates
with open("../indexing/data/pid2docsauthored.pickle", "rb") as infile:
    pid2docsauthored = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading draft2mls.")
# get tfidf representations for candidates
with open("../indexing/data/draft2mls.pickle", "rb") as infile:
    draft2mls = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading email2pid.")
# get tfidf representations for candidates
with open("../indexing/data/email2pid.pickle", "rb") as infile:
    email2pid = pickle.load(infile)
print(len(pid2tfidfvec))

print("Loading pid2email.")
# get tfidf representations for candidates
with open("../indexing/data/pid2email.pickle", "rb") as infile:
    pid2email = pickle.load(infile)
print(len(pid2tfidfvec))




print("All done ^_^!")







# scheme 1 -- cosine similarity on the test vectors (train vectors not used)
from scipy.spatial.distance import cosine as cosine_distance
import math
class CosineRanker:
    def __init__(self, rep):
        draft2vec, pid2vec = rep
        self.d2v = draft2vec
        self.p2v = pid2vec
    
    def score(self, test_example):
        scores = []
        draft_name, ranked_list = test_example
        dv = self.d2v[draft_name]
        for pid in ranked_list:
            if pid in self.p2v:
                pv = self.p2v[pid]
                score = 1 - cosine_distance(dv, pv)
            else:
                print("CANT FIND PARTICIPANT IN REPRESENTATION FILE!")
                score = 0

            if math.isnan(score):
                score = 0
            scores.append(score)
        print(scores)
        return scores




class IETF_recommender_API:
    def __init__(self):
        self.representations = {"LDA":(draft2ldavec, pid2ldavec), "TFIDF":(draft2tfidfvec, pid2tfidfvec)}
        self.rankers = {"LDA": CosineRanker(self.representations["LDA"]), "TFIDF": CosineRanker(self.representations["TFIDF"])}
        
    def _format_results(self, pid_list):
        output = ""
        i = 0
        output += "<table>"
        output += " <tr>"
        output += " <th style='width:90%; text-align: left; background-color: rgba(0,0,255,0.7); color: white;' >Participant</th>"
        output += " <th style='font-size:12; background-color: rgba(0,0,255,0.7); color: white;'>(Optional) Feedback</th>"
        output += " </tr>"
             
        for pid in pid_list:
             i += 1
             if i > 5:
                 break
             color_val =  "0.1" if i % 2 == 1 else "0.15"
             name = pid2name[pid]           
             #dt_link = "https://datatracker.ietf.org/api/v1/person/person/?id=" + str(pid)
             dt_link = "https://datatracker.ietf.org/person/" + pid2email[pid]
             
             name_html = "<a href = '" + dt_link +  "' style='font-size:24;'>" + name + "</a>"
             
             if pid in pid2docsauthored:
                 docs_authored = pid2docsauthored[pid]
             else:
                 docs_authored = []
             if len(docs_authored) > 5:
                 docs_authored = docs_authored[:5]
             docs_html = ""
             for d in docs_authored:
                 docs_html += "<a href = 'https://datatracker.ietf.org/doc/" + d +  "/'> " + d + "</a>; &nbsp; "
             docs_html += "<br>"  

                      
             output +=" <tr>"
             output +="    <td style='background-color: rgba(0,0,255," + color_val + ");'>" + name_html + "<br><br> Some authored drafts: " + docs_html  + " </td>"
 
             output +="  <td style='background-color: rgba(0,0,255," + color_val + ");'><select style='width:100px;' name='candfeedback-" + str(pid)  +  "' id='candfeedback' class='candfeedback'onchange = 'log_to_server();'>  "
             output +="  <option value='none'>-</option>"
             output +="  <option value='NotUseful'>Not useful</option>"
             output +="  <option value='PartiallyUseful'>Partially useful</option>"
             output +="  <option value='Useful'>Useful</option>"
             output += " </select></td></tr>"
        output += "</table>"
        return output
    
    def _combine_results(self, res1, res2): # IMPORTANT: it is assumed res1 and res2 are sorted from best to worst
        assert len(res1) == len(res2)

        combined = []
        res1_pids = [x[0] for x in res1]
        res2_pids = [x[0] for x in res2]
        for i in range(len(res1)):
            current_pid = res1_pids[i]
            rankin1 = i
            rankin2 = res2_pids.index(current_pid)
            combined.append((current_pid, rankin1 + rankin2))
        return combined
            
            



    def search_default(self, draft_name, model_id):
        backoff = False
        if draft_name not in draft2mls:
            backoff = True
        else:
            mls_mentioning_draft = draft2mls[draft_name]
            candidate_pids = set()
            for ml in mls_mentioning_draft:
                for pid in ml2activepids[ml]:
                    candidate_pids.add(pid)
            if len(candidate_pids) < 5:
                backoff = True
  
        if backoff:            
            candidate_pids = set()
            for ml in ml2activepids:
                for pid in ml2activepids[ml]:
                    candidate_pids.add(pid)
        
        data_for_ranker = [x for x in candidate_pids]
        example_set = draft_name, data_for_ranker
        
        scores = self.rankers[model_id].score(example_set)

        results = zip(data_for_ranker, scores)

        results = sorted(results, key = lambda x:x[1], reverse = True) 
        
        output_pids =  [x[0] for x in results] # the html generating function expects just the pids
 
        string_output = self._format_results(output_pids)

        return string_output

    def _get_person_vector(self, p, m):
        #print("TRYING TO GET PERSON VECTOR")
        try:
            if m == "LDA":
                return pid2ldavec[p]
            if m == "TFIDF":
                return pid2tfidfvec[p]
        except:
            #print("Failed")
            return None
            
    def search_area(self, draft_name, area_acronym, model_id):
        candidate_pids = set()
        for ml in ml2activepids:
            for pid in ml2activepids[ml]:
                candidate_pids.add(pid)

        data_for_ranker = [x for x in candidate_pids]
        example_set = draft_name, data_for_ranker
        
        print(len(example_set))
        scores1 = self.rankers[model_id].score(example_set)
        results1 = zip(data_for_ranker, scores1)
        results1 = sorted(results1, key = lambda x:x[1], reverse = True) 
        print(len(results1))
        scores2 = []
        for pid in data_for_ranker:
            norm = sum(pid2areavectors[pid].values())
            if norm < 20:
                scores2.append(0)
                continue
            if area_acronym in pid2areavectors[pid]:
                scores2.append(pid2areavectors[pid][area_acronym]/norm)
            else:
                scores2.append(0)

        results2 = zip(data_for_ranker, scores2)
        results2 = sorted(results2, key = lambda x:x[1], reverse = True) 
        print(len(results2))
        final_results = self._combine_results(results1, results2)
        final_results = sorted(final_results, key = lambda x:x[1], reverse = False) # here smaller rank is better, that's why no reversing

        output_pids =  [x[0] for x in final_results] # the html generating function expects just the pids
 
        string_output = self._format_results(output_pids)

        return string_output

    def search_complementary(self, draft_name, avoid_names, model_id):
        # transform avoid names to avoid_pids
        avoid_pids = []
        for avoid_name in avoid_names.split(","):
            start = avoid_name.index("(")
            end = avoid_name.index(")")
            avoid_email = avoid_name[start+1:end]
            print(avoid_email)
            if avoid_email in email2pid:
                print("FOUND")
                avoid_pids.append(email2pid[avoid_email])        

        # ***********************
        candidate_pids = set()
        for ml in ml2activepids:
            for pid in ml2activepids[ml]:
                candidate_pids.add(pid)

        data_for_ranker = [x for x in candidate_pids]
        example_set = draft_name, data_for_ranker
        
        print(len(example_set))
        scores1 = self.rankers[model_id].score(example_set)
        results1 = zip(data_for_ranker, scores1)
        results1 = sorted(results1, key = lambda x:x[1], reverse = True) 
        print(len(results1))


        norm_const = 0
        avoid_vector = None
        for apid in avoid_pids:
            if avoid_vector is None:
                avoid_vector = self._get_person_vector(apid, model_id)
                norm_const += 1
            else:
                another_avoid_vector = self._get_person_vector(apid, model_id)
                if another_avoid_vector is not None:
                    avoid_vector += another_avoid_vector            
                    norm_const += 1
        
        if avoid_vector is not None:
            avoid_vector /= norm_const

        scores2 = []
        for pid in data_for_ranker:
            person_vector = self._get_person_vector(pid, model_id)
            if avoid_vector is None or person_vector is None :
                score = 0
            else:
                score = cosine_distance(avoid_vector, person_vector) # here bigger distance is more complementary
            scores2.append(score)

        print(avoid_vector)        
        results2 = zip(data_for_ranker, scores2)
        results2 = sorted(results2, key = lambda x:x[1], reverse = True) 
        print(len(results2))
        final_results = self._combine_results(results1, results2)
        final_results = sorted(final_results, key = lambda x:x[1], reverse = False) # here smaller rank is better, that's why no reversing

        output_pids =  [x[0] for x in final_results] # the html generating function expects just the pids
 
        string_output = self._format_results(output_pids)

        return string_output

    
print(list(pid2ldavec.keys())[:10])

r = IETF_recommender_API()

#html = r.search_default("draft-petithuguenin-tsvwg-stun-pmtud","TFIDF")
html = r.search_default("draft-petithuguenin-formal-fsm","TFIDF")
print(html)

#html = r.search_complementary("draft-zia-route", [117099, 122623,  1234840], "LDA")
#print(html)



























